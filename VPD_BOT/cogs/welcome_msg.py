"""import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time


class welcome_msg(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def _load_config(self):
            config = configparser.ConfigParser()
            configFilePath = r'config.cfg'
            config.read(configFilePath)
            return config
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        config = self._load_config()
        enable_welcome_message = config.getboolean("Welcome Message","enable_welcome_message")
        if not enable_welcome_message:
            return
        
        welcome_channel_id = config.getint("Welcome Message","welcome_channel_id")
        welcome_channel = self.bot.get_channel(welcome_channel_id)
        if welcome_channel is None:
            print(f"Welcome channel with ID {welcome_channel_id} not found.")
            return
        
        embed = discord.Embed(
            title="VicePD",
            description=f"Willkommen {member.mention}, auf **VicePD**! \n\n Bitte lese dir das <#1442279753707946215> durch. Die Einhaltung der Regeln stellt sicher, dass der Server ein freundlicher und unterhaltsamer Ort für alle ist und bleibt. \n\n Viel Spaß auf VicePD!",
            color=discord.Color.grey(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_image(url="https://i.imgur.com/iu1VyKZ.png")
        embed.set_footer(text=f"Member ID: {member.id}")
        
        self.bot.loop.create_task(welcome_channel.send(embed=embed))
        #await welcome_channel.send(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(welcome_msg(bot))"""