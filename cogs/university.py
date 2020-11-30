from difflib import get_close_matches

import discord
from discord.ext import commands

import utils
from constants import OFFICES


class University(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(
        aliases=['γραφείο', 'γραφειο', 'grafeio'],
        brief="Find out in which office you can find a professor"
    )
    async def office(self, ctx: commands.Context, name):
        """office [name]"""
        matches = get_close_matches(name, OFFICES)
        if matches:
            await ctx.send(f"{matches[0]}: {OFFICES[matches[0]]}")
        else:
            await ctx.send(f"Δεν ξερω που ειναι το γραφειο του {name}")

    @commands.command(
        aliases=["πρόγραμμα", "προγραμμα", "programma", "program"],
        brief="See the classes or the exams schedule"
    )
    async def schedule(self, ctx: commands.Context, arg):
        """schedule [classes/exams]"""
        arg = arg.lower()
        if arg in ["μαθηματων", "μαθημάτων", "mathimatwn", "classes"]:
            to_fetch = "ωρολόγιο πρόγραμμα"
        elif arg in ["εξεταστικης", "εξεταστικής", "eksetastikis", "exams"]:
            to_fetch = "πρόγραμμα εξεταστικής"
        else:
            await ctx.send("Invalid argument")
            return

        title, link = await utils.fetch_schedule(to_fetch, self.bot.aiohttp_session)

        if title is not None:
            embed = discord.Embed(title=title, description=link, color=0x239fcf)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Site is down :/")


def setup(bot):
    bot.add_cog(University(bot))
