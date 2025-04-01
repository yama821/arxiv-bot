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

if __name__ == "__main__":

    load_dotenv(Path(__file__).resolve().parent / '.env')

    query = "cat:math.CO"
    arxiv_client = ArxivClient()
    search_results = arxiv_client.sync_search(query, max_results=10)

    llm_client = LLMClient()
    ocr_client = MistralOCR()
    notion_client = NotionClient()
    converter = MarkdownToNotionConverter()
    
    for i, result in tqdm(enumerate(search_results)):
        
        pdf_url = result.pdf_url
        pdf_url = pdf_url[:4] + "s" + pdf_url[4:]
        print(f"[{i+1}/{len(search_results)}]: {pdf_url}")
        print(f"\ttitle: {result.title}")
        markdown_text = ocr_client.render_md(pdf_url)

        print("\tsummarizing...")
        summary = llm_client.summarize_math_paper(markdown_text)
        json_data = converter.parse(markdown_text=summary)

        print("\tcreate page...")
        page_id = notion_client.create_page(result.title, url=result.entry_id)
        notion_client.create_children(json_data['results'], page_id)

        # webhook = DiscordWebhookSender()
#         authors = ", ".join([author.name for author in result.authors])
#         webhook.send_embed(
#             author=f"論文紹介 {datetime.today().date()} ({i+1}/{len(search_results)})",
#             title=f"__{result.title}__",
#             description=f"""
# * 著者: {authors}
# * リンク: {result.entry_id}
# * 投稿日: {result.published.date()}
# ### アブストラクト:\n{result.summary}
# """,
#             color=Color.BLUE,
#         )
