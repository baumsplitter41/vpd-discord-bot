import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv

class greet(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot



#Command initialization
    @slash_command(description="Greet a User")
    async def greet(self, ctx, user: str = Option(discord.User, "The user, you want to greet")):
        await ctx.respond(f"Hello {user.mention}")


def setup(bot: discord.Bot):
    bot.add_cog(greet(bot))
