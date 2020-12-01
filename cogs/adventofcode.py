import json

import discord
from discord.ext import commands, tasks

from constants import AOC_JOIN, AOC_ID, AOC_SESSION


class AdventOfCode(commands.Cog, name="Set Up"):
    def __init__(self, bot):
        self.bot = bot
        self.lb = {}
        self.lb_url = "https://adventofcode.com/2020/leaderboard/private/view/{aoc_id}.json"

        with open("data/aoc_users.json", "r") as f:
            self.users = json.load(f)

        self.update_lb.start()
        self.save_users.start()

    def cog_unload(self):
        self.save_users.cancel()
        self.update_lb.cancel()

    @tasks.loop(seconds=10)
    async def save_users(self):
        with open("data/aoc_users.json", "w") as f:
            json.dump(self.users, f, indent=4)

    @tasks.loop(minutes=20)
    async def update_lb(self):
        cookies = {"session": AOC_SESSION}
        url = self.lb_url.format(aoc_id=AOC_ID)
        async with self.bot.aiohttp_session.get(url, cookies=cookies) as r:
            if r.status != 200:
                # We will try again in 20 minutes
                return
            text = await r.json()

        self.lb = text["members"]
        await self.update_users()

    @update_lb.before_loop
    async def before_update_lb(self):
        await self.bot.wait_until_ready()

    async def update_users(self):
        # guild = self.bot.get_guild(502466330432110592)
        guild = self.bot.get_guild(669328482857385985)
        if guild is None:
            return

        for mem_id, user in self.users.items():
            aoc_id = user["aoc_id"]
            og_name = user["og_name"]
            stars = self.lb[aoc_id]
            member = guild.get_member(int(mem_id))
            await member.edit(nick=f"{og_name} ⭐{stars}")

    @commands.group(name="adventofcode", aliases=["aoc"])
    async def adventofcode(self, ctx: commands.Context):
        """All of the Advent of Code commands."""
        if not ctx.invoked_subcommand:
            await ctx.send("Available subcommands:\n"
                           "`about`\n"
                           "`join`\n"
                           "`leaderboard`\n"
                           "`claim`\n"
                           "`verify`\n")

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

    @adventofcode.command(aliases=["lb", "board"], brief="Get a link for out leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        await ctx.send("See our leaderboard here: "
                       "https://adventofcode.com/2020/leaderboard/private/view/498817")

    @adventofcode.command(
        brief="Link your Advent of Code account to your Discord account.\n"
              "You can find your Advent of Code user ID on the settings page of the Advent of Code website; "
              "it's your anonymous user number: (anonymous user #YOUR_AOC_USER_ID)"
    )
    async def claim(self, ctx: commands.Context, aoc_id):
        """claim [aoc id]"""
        if ctx.author.id in self.users:
            await ctx.send("You have already claimed an AoC account.")
            return

        og_name = ctx.author.display_name
        if aoc_id not in self.lb:
            stars = 0
        else:
            stars = self.lb[aoc_id]["stars"]

        self.users[str(ctx.author.id)] = {"aoc_id": aoc_id, "og_name": og_name}

        await ctx.author.edit(nick=f"{og_name} ⭐{stars}")

    @adventofcode.command(brief="Verify that the stars in the name of a user are correct")
    async def verify(self, ctx: commands.Context, member: discord.Member = None):
        """verify (member)"""
        member = member or ctx.author
        if str(member.id) not in self.users:
            await ctx.send(f"{member.display_name} has not claimed an AoC account")
            return

        aoc_id = self.users[str(member.id)]["aoc_id"]
        needs_fixing = False
        should_have = self.lb[aoc_id]["stars"]
        try:
            has = member.display_name.split("⭐")[1]
        except IndexError:
            needs_fixing = True
        else:
            needs_fixing = has.strip() != str(should_have)

        if needs_fixing:
            og_name = self.users[str(member.id)]["og_name"]
            await member.edit(nick=f"{og_name} ⭐{should_have}")
            await ctx.send("The error has been fixed and the stars are correct now")
        else:
            await ctx.send("The stars are good")


def setup(bot):
    bot.add_cog(AdventOfCode(bot))
