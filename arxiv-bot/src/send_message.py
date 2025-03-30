import discord
import config
import os

bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(guild_ids=config.GUILD_IDS)
async def hello(ctx):
    await ctx.respond("Hello!")


discord_token = os.environ["DISCORD_TOKEN"]
bot.run(discord_token)
