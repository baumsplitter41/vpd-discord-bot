import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv

class say(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot



#Command initialization
    @slash_command(description="Let the bot send a message")
    async def say(
            self,
            ctx,
            text: str = Option(description="Input the text you want to send"),
            channel_input: discord.TextChannel = Option(description="Select the channel,where you want to send the message.")
    ):  
        channel= discord.utils.get(ctx.guild.channels, id = int(channel_input[2:-1]))
        await channel.send(text)
        await ctx.respond("Message sent", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(say(bot))
