import discord
from discord.ext import commands
from discord.commands import slash_command


class Hello(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(name="hallo", description="hello")
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Hey {ctx.author.mention}")


def setup(bot: discord.Bot):
    bot.add_cog(Hello(bot))
