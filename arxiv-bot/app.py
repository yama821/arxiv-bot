from llm_client import LLMClient
from ocr import MistralOCR
from search import ArxivClient
from send_message import DiscordWebhookSender, Color
from datetime import datetime

if __name__ == "__main__":

    query = "cat:math.CO"
    arxiv_client = ArxivClient()
    search_results = arxiv_client.sync_search(query, max_results=10)

    
    for i, result in enumerate(search_results):

        llm_client = LLMClient()
        # summary = llm_client.generate_with_system_prompt('translate_abstruct', result.summary)

        webhook = DiscordWebhookSender()

        authors = ", ".join([author.name for author in result.authors])
        webhook.send_embed(
            author=f"論文紹介 {datetime.today().date()} ({i+1}/{len(search_results)})",
            title=f"__{result.title}__",
            description=f"""
* 著者: {authors}
* リンク: {result.entry_id}
* 投稿日: {result.published.date()}
### アブストラクト:\n{result.summary}
""",
            color=Color.BLUE,
        )
