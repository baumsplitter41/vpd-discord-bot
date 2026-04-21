import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time
import asyncio


class autodelmsg(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    def _get_info_channel(self):
        config = self._load_config()
        channel_ids = [int(channel_id.strip()) for channel_id in config.get("Moderation")("autodelete_channel_id").split(",")]
        channels = [self.bot.get_channel(channel_id) for channel_id in channel_ids]
        if any(channel is None for channel in channels):
            print(f"One or more roles with IDs {channel_ids} not found.")
            return
        return channels
    def _get_message_age_limit(self):
        config = self._load_config()
        return config.getint("Moderation", "autodelete_message_age")
    


    @commands.Cog.listener()
    async def on_ready(self):
        channels = self._get_info_channel()
        if channels is None:
            return
        message_age_limit = self._get_message_age_limit()
        while True:
            for channel in channels:
                async for message in channel.history(limit=None):
                    if (time.time() - message.created_at.timestamp()) > (message_age_limit * 3600):
                        try:
                            await message.delete()
                            print(f"Deleted message from {message.author} in {channel.name} due to age.")
                        except Exception as e:
                            print(f"Failed to delete message: {e}")
            await asyncio.sleep(3600) #Check every hour


def setup(bot: discord.Bot):
    bot.add_cog(autodelmsg(bot))