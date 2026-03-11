import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time


class einweisungping(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def _load_config(self):
            config = configparser.ConfigParser()
            configFilePath = r'config.cfg'
            config.read(configFilePath)
            enable_channel_ping_on_einweisung = config.getboolean("Einweisung", "enable_channel_ping_on_einweisung")
            if not enable_channel_ping_on_einweisung:
                return
            return config            
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        config = self._load_config()
        
        channel_ping_id = config.getint("Einweisung", "channel_ping_id")
        channel_ping = self.bot.get_channel(channel_ping_id)
        if channel_ping is None:
            print(f"Channel with ID {channel_ping_id} not found.")
            return
        channel_join_id = config.getint("Einweisung", "channel_join_id")
        channel_join = self.bot.get_channel(channel_join_id)
        if channel_join is None:
            print(f"Channel with ID {channel_join_id} not found.")
            return
        
        ping_role_ids = [int(role_id.strip()) for role_id in config.get("Einweisung", "ping_role_id").split(",")]
        ping_roles = [member.guild.get_role(role_id) for role_id in ping_role_ids]
        if any(role is None for role in ping_roles):
            print(f"One or more roles with IDs {ping_role_ids} not found.")
            return
        
        if after.channel is not None:
            if after.channel.id == channel_join_id: 
                ping_message = f"{' '.join(role.mention for role in ping_roles)} {member.mention} ist dem Einweisungskanal beigetreten!"
                await channel_ping.send(ping_message)
        

        



def setup(bot: discord.Bot):
    bot.add_cog(einweisungping(bot))