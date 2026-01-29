import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time


class antispam(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = configparser.ConfigParser()
        config.read('config.cfg')
        spamindex = int(config.get('Moderation', 'Spam_Sensitivity_Index').split('#')[0].strip())
        message_content = message.content.lower()
        team_role_ids = [int(role_id) for role_id in config.get('Moderation', 'Mod_role_IDs').split(',') if role_id.strip().isdigit()]



        author_roles = [role.id for role in message.author.roles]
        if any(role_id in author_roles for role_id in team_role_ids):
            return
        current_time = time.time()
        if not hasattr(self, 'user_message_times'):
            self.user_message_times = {}
        if message.author.id not in self.user_message_times:
            self.user_message_times[message.author.id] = []
        self.user_message_times[message.author.id].append(current_time)
        self.user_message_times[message.author.id] = [t for t in self.user_message_times[message.author.id] if current_time - t <= 10]
        if len(self.user_message_times[message.author.id]) > spamindex:
            try:
                await message.delete()
                warning_msg = f"{message.author.mention}, you are sending messages too quickly. Please slow down."
                await message.channel.send(warning_msg, delete_after=5)
            except discord.Forbidden:
                print("Missing permissions to delete messages.")


def setup(bot: discord.Bot):
    bot.add_cog(antispam(bot))