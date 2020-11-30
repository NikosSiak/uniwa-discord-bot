from discord.ext import commands

from constants import AOC_JOIN

class AdventOfCode(commands.Cog, name="Set Up"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="adventofcode", aliases=["aoc"])
    async def adventofcode(self, ctx: commands.Context):
        """All of the Advent of Code commands."""
        if not ctx.invoked_subcommand:
            await ctx.send("Available subcommands:\n"
                           "`about`\n"
                           "`join`\n")

    @adventofcode.command(brief="Get info about the Advent of Code")
    async def about(self, ctx: commands.Context):
        """about"""
        about_url = "https://adventofcode.com/2020/about"
        about_txt = "The Advent of Code is a yearly event that takes place in December with daily christmas themed " \
                    "programming challenges of varying difficulty that you can solve in any language you want.\n" \
                    f"For more see: {about_url}"
        await ctx.send(about_txt)

    @adventofcode.command(brief="Get the code for our private leaderboard")
    async def join(self, ctx: commands.Context):
        """join"""
        await ctx.author.send(f"Go to https://adventofcode.com/2020/leaderboard/private "
                              f"and join with our code: `{AOC_JOIN}`")


def setup(bot):
    bot.add_cog(AdventOfCode(bot))
