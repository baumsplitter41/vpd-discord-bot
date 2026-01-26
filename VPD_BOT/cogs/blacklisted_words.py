import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class blacklist_words(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = configparser.ConfigParser()
        config.read('config.ini')
        blacklist_words_words = config.get('Moderation', 'Blacklist_Words_List').split(',')
        blacklist_words_words = [word.strip().lower() for word in blacklist_words_words]
        team_role_ids = [int(role_id) for role_id in config.get('Moderation', 'Mod_role_IDs').split(',') if role_id.strip().isdigit()]
        author_roles = [role.id for role in message.author.roles]
        if any(role_id in author_roles for role_id in team_role_ids):
            return

        for word in blacklist_words_words:
            if word in message.content.lower():
                try:
                    await message.delete()
                    warning_msg = f"{message.author.mention}, your message was removed due to the use of prohibited language."
                    await message.channel.send(warning_msg, delete_after=5)
                except discord.Forbidden:
                    print("Missing permissions to delete messages.")
                break

def setup(bot: discord.Bot):
    bot.add_cog(blacklist_words(bot))