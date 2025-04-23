from llm_client import LLMClient
from ocr import MistralOCR
from search import ArxivClient
from send_message import DiscordWebhookSender, Color
from datetime import datetime
from notion import NotionClient
from md_parser import MarkdownToNotionConverter
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path
import arxiv_feed_parser as afp


def execute(cat):
    retriever = afp.retrieve(cat, None)

    llm_client = LLMClient()
    ocr_client = MistralOCR()
    notion_client = NotionClient()
    converter = MarkdownToNotionConverter()
    
    paper_count = len(retriever.newsubmissions)
    print(f"find {paper_count} new papers! (cat:{cat})")

    paper_info = []
    for i, result in tqdm(enumerate(retriever.newsubmissions)):

        pdf_url = result["pdf_url"]
        print(f"[{i+1}/{paper_count}]: {pdf_url}")
        print(f"\ttitle: {result['title']}")
        markdown_text = ocr_client.render_md(pdf_url)

        print("\tsummarizing...")
        summary = llm_client.summarize_math_paper(markdown_text)
        json_data = converter.parse(markdown_text=summary)

        short_summary = llm_client.generate_with_system_prompt(
            prompt_type='gen_short_summary',
            input_text=summary,
        )

        print(f"\tshort summary: {short_summary}")

        print("\tcreate page...")
        properties = {
            "URL": {"type": "url", "url": result["abs_url"]},
            "primary_category": {"type": "select", "select": {"name": result["primary_subject"]}},
            "published": {"type": "date", "date": {"start": result["published"].date().strftime("%Y-%m-%d")}},
        }
        page_id = notion_client.create_page(result["title"], properties=properties)

        notion_client.create_child({
            "object": "block", 
            "type": "heading_1", 
            "heading_1": {
                "rich_text": [{
                    "type": "text", 
                    "text": {"content": "LLM による要約結果"}
                }],
            }
        }, page_id)
        notion_client.create_children(json_data['results'], page_id)

        notion_url = notion_client.retrieve_page(page_id)['url']

        paper_info.append({
            "title": result["title"],
            "abs_url": result["abs_url"],
            "authors": result["authors"],
            "published": result["published"],
            "abstract": result["abstract"],
            "notion_url": notion_url
        })

    for i, result in enumerate(paper_info):
        webhook = DiscordWebhookSender()
        webhook.send_embed(
            author=f"論文紹介 {datetime.today().date()} ({i+1}/{paper_count})",
            title=f"__{result['title']}__",
            description=f"""
* 著者　 : {result['authors']}
* リンク : {result['abs_url']}
* 投稿日 : {result['published'].date()}
* Notion: {result['notion_url']}
{result['abstract']}
""",
            color=Color.BLUE,
        )


if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent / '.env')

    cats = ['math.CO', 'cs.DS']

    for cat in cats:
        execute(cat)
