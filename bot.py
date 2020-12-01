import os

import discord
from discord.ext import commands
import aiohttp

TOKEN = open('data/TOKEN.txt', 'r').readline().strip()

intents = discord.Intents.default()  # even default is more than we actually need
intents.members = True  # For AoC
bot = commands.Bot(command_prefix=";", intents=intents, owner_ids=[420338564354801664, 185725754821050368])
bot.remove_command('help')


async def create_aiohttp_session():
    bot.aiohttp_session = aiohttp.ClientSession(loop=bot.loop)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print('------')


for cog in os.listdir("./cogs"):
    if cog.endswith(".py") and not cog.startswith("_"):
        try:
            cog = f"cogs.{cog.replace('.py', '')}"
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} can not be loaded:")
            raise e
bot.load_extension("jishaku")

bot.loop.run_until_complete(create_aiohttp_session())
bot.run(TOKEN)
