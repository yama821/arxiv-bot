# app.py
from llm_client import LLMClient
from ocr import MistralOCR
from send_message import DiscordWebhookSender, Color
from datetime import datetime
from notion import NotionClient
from md_parser import MarkdownToNotionConverter
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path
import arxiv_feed_parser as afp

import argparse
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, unquote

from search import ArxivClient


# ======== 非 arXiv PDF 用の簡易メタデータ ========

def build_generic_pdf_metadata(pdf_url: str) -> Dict[str, Any]:
    """
    arXiv ではない PDF リンク用の簡易メタデータ。
    タイトルなどは URL のファイル名からそれっぽく生成。
    """
    parsed = urlparse(pdf_url)
    filename = unquote(parsed.path).rstrip("/").split("/")[-1]

    if not filename:
        title_base = "Unknown title"
    else:
        if filename.lower().endswith(".pdf"):
            title_base = filename[:-4]
        else:
            title_base = filename

    title = title_base.replace("_", " ").replace("-", " ")

    return {
        "title": title or "Unknown title",
        "abs_url": pdf_url,  # 別ページはないので PDF URL をそのまま
        "pdf_url": pdf_url,
        "primary_subject": "unknown",
        "published": datetime.today(),
        "authors": "Unknown authors",
        "abstract": "",
    }


# ======== 共通パイプライン ========

def run_pipeline(results: List[Dict[str, Any]], source_label: Optional[str] = None) -> None:
    """
    「論文メタデータ dict のリスト」を受け取り、
    OCR → LLM 要約 → Notion → Discord までをまとめて実行する。
    dict は次のキーを持つ前提：
      - title
      - abs_url
      - pdf_url
      - primary_subject
      - published (datetime)
      - authors
      - abstract
    """
    llm_client = LLMClient()
    ocr_client = MistralOCR()
    notion_client = NotionClient()
    converter = MarkdownToNotionConverter()

    paper_count = len(results)
    if source_label:
        print(f"find {paper_count} new papers! ({source_label})")
    else:
        print(f"find {paper_count} new papers!")

    paper_info: List[Dict[str, Any]] = []

    for i, result in tqdm(list(enumerate(results, start=1)), total=paper_count):
        pdf_url = result["pdf_url"]
        print(f"[{i}/{paper_count}]: {pdf_url}")
        print(f"\ttitle: {result['title']}")

        # OCR → markdown
        markdown_text = ocr_client.render_md(pdf_url)

        # LLM 要約
        print("\tsummarizing...")
        summary = llm_client.summarize_math_paper(markdown_text)
        json_data = converter.parse(markdown_text=summary)

        short_summary = llm_client.generate_with_system_prompt(
            prompt_type="gen_short_summary",
            input_text=summary,
        )

        print(f"\tshort summary: {short_summary}")

        # Notion page 作成
        print("\tcreate page...")
        properties = {
            "URL": {"type": "url", "url": result["abs_url"]},
            "primary_category": {
                "type": "select",
                "select": {"name": result["primary_subject"]},
            },
            "published": {
                "type": "date",
                "date": {
                    "start": result["published"].date().strftime("%Y-%m-%d")
                },
            },
        }
        page_id = notion_client.create_page(
            result["title"], properties=properties
        )

        notion_client.create_child(
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "LLM による要約結果"},
                        }
                    ],
                },
            },
            page_id,
        )
        notion_client.create_children(json_data["results"], page_id)

        notion_url = notion_client.retrieve_page(page_id)["url"]

        paper_info.append(
            {
                "title": result["title"],
                "abs_url": result["abs_url"],
                "authors": result["authors"],
                "published": result["published"],
                "abstract": result["abstract"],
                "notion_url": notion_url,
                "short_summary": short_summary,
            }
        )

    # Discord 通知
    for i, info in enumerate(paper_info, start=1):
        webhook = DiscordWebhookSender()
        webhook.send_embed(
            author=f"論文紹介 {datetime.today().date()} ({i}/{paper_count})",
            title=f"__{info['title']}__",
            description=f"""
* 著者　 : {info['authors']}
* リンク : {info['abs_url']}
* 投稿日 : {info['published'].date()}
* Notion: {info['notion_url']}

{info['short_summary']}
""",
            color=Color.BLUE,
        )

    print("========== OPENAI USED TOKENS ============")
    print(f"Input Tokens : {llm_client.used_input_tokens}")
    print(f"Output Tokens: {llm_client.used_output_tokens}")


# ======== エントリ関数（カテゴリ / URL） ========

def execute_from_category(cat: str, top_k: int = 100) -> None:
    """
    arxiv_feed_parser を使って new submissions を取りに行くモード。
    （既存の使い方）
    """
    retriever = afp.retrieve(cat, None)
    results = [result for result in retriever.newsubmissions]
    results = results[:top_k]
    run_pipeline(results, source_label=f"cat:{cat}, top_k:{top_k}")


def execute_from_url(url: str, arxiv_client: Optional[ArxivClient] = None) -> None:
    """
    URL 1 個だけを指定して処理するモード。
    - arxiv abs URL
    - arxiv pdf URL
    - 非 arxiv の PDF URL
    に対応。
    """
    if arxiv_client is None:
        arxiv_client = ArxivClient()

    if "arxiv.org" in url:
        result = arxiv_client.get_metadata_from_url(url)
    else:
        result = build_generic_pdf_metadata(url)

    run_pipeline([result], source_label=f"url:{url}")


# ======== CLI エントリポイント ========

if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent / ".env")

    parser = argparse.ArgumentParser(
        description="Fetch papers, summarize, save to Notion, and notify Discord."
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Single paper URL (arXiv abs/pdf or non-arXiv PDF).",
    )
    parser.add_argument(
        "--cat",
        nargs="*",
        help="arXiv categories (e.g. math.CO). Multiple categories allowed.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of new submissions per category to process (default: 3).",
    )

    args = parser.parse_args()

    # 1. 単一 URL モード
    if args.url:
        execute_from_url(args.url)

    # 2. カテゴリモード（従来どおり）
    else:
        cats = args.cat or ["math.CO"]
        top_k = args.top_k
        for cat in cats:
            execute_from_category(cat, top_k=top_k)
