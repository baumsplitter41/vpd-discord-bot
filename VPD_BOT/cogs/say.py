import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv

class Say(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    intents.reactions = True

    client = discord.Client(intents=intents)
    debug_guilds_up = []
    server_token = os.getenv("SERVER").split(",")
    for i in range(len(server_token)):
        debug_guilds_up.append(int(server_token[i]))
    
    bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="VicePD Bot",
    intents=intents,
    debug_guilds=debug_guilds_up if debug_guilds_up else None
    )


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
    bot.add_cog(Say(bot))
