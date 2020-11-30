import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(brief="See the profile picture of a user")
    async def pfp(self, ctx: commands.Context, member: discord.Member):
        """pfp (member)"""
        member = member or ctx.author
        await ctx.send(member.avatar_url)


def setup(bot):
    bot.add_cog(Misc(bot))
