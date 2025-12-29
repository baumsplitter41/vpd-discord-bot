import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command


class Say(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(description="Greet a User")
    async def greet(ctx, user: str = Option(discord.User, "The user, you want to greet")):
        await ctx.respond(f"Hello {user.mention}")


def setup(bot: discord.Bot):
    bot.add_cog(Say(bot))
