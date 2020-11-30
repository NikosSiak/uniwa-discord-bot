from discord.ext import commands


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, (commands.BadArgument, commands.MissingRequiredArgument)):
            await ctx.send("Invalid or missing arguments")
        elif isinstance(exception, commands.CheckFailure):
            await ctx.send("You don't have the required permissions to run this command.")
        elif isinstance(exception, commands.CommandNotFound):
            print(f"Command {ctx.message.content} not found")
            return

        raise exception


def setup(bot):
    bot.add_cog(Errors(bot))
