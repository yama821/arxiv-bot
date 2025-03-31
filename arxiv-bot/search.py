import arxiv
import discord
from discord.ext import commands
import os
import asyncio

from llm_client import LLMClient

class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
    
    def sync_search(self, query) -> list[arxiv.Result]:
        search_state = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        results = list(self.client.results(search_state))
        return results
    
    async def search(self, query) -> list[arxiv.Result]:
        # ブロッキングな検索処理を別スレッドで実行
        return await asyncio.to_thread(self.sync_search, query)


class ArxivCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.arxiv_client = ArxivClient()
        self.llm_client = LLMClient()

    @discord.slash_command(name="search", description="search arXiv by query")
    async def search(self, ctx: discord.ApplicationContext, query: str):

        results: list[arxiv.Result] = await self.arxiv_client.search(query)
        for i, result in enumerate(results):
            embed = discord.Embed(
                title=f"Search Results ({i+1}/{len(results)})",
                description=f"[search query]: {query}",
                color=discord.Colour.green()
            )

            await ctx.respond(embed=embed)

            authors = ", ".join([author.name for author in result.authors])

            summary = await self.llm_client.generate_with_system_prompt('translate_abstruct', result.summary)
            print(summary)
            embed.add_field(
                name=f"__{result.title}__",
                value=f"Published: {result.published}\n[Link]({result.pdf_url})\nAuthors: {authors}\n\n概要:\n{summary}",
                inline=False
            )
            await ctx.edit(embed=embed)
            # break
        
if __name__ == "__main__":
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!")
    bot.add_cog(ArxivCog(bot))
    
    discord_token = os.environ["DISCORD_TOKEN"]
    bot.run(discord_token)
