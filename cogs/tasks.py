import discord
from discord.ext import commands, tasks

import utils
from constants import ANNOUNCE_CHN_ID


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.post_announcements.start()

    @tasks.loop(hours=5)
    async def post_announcements(self):
        announcements = await utils.fetch_notifications(self.bot.aiohttp_session)

        chn = self.bot.get_channel(ANNOUNCE_CHN_ID)
        if chn is not None:
            if len(announcements) > 0:
                await chn.send(f"{len(announcements)} νέ{'ες ' if len(announcements) > 1 else 'α '}"
                               f"{'ανακοινώσεις' if len(announcements) > 1 else 'ανακοίνωση'} @everyone")

            for announcement in announcements:
                embed = discord.Embed(title=announcement[0], description=announcement[1], color=0x239fcf)

                await chn.send(embed=embed)

    @post_announcements.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))
