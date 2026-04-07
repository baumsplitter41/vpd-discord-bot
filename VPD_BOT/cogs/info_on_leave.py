import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time

#Gives supervisors an information, when a department member leaves the server.

class infoleaving(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    def _get_info_channel(self):
        config = self._load_config()
        info_channel_id = int(config["Einweisung"]["info_channel_id"])
        info_channel = self.bot.get_channel(info_channel_id)
        if info_channel is None:
            print(f"Log channel with ID {info_channel_id} not found.")
            return None
        return info_channel
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        config = self._load_config()
        enable_info = config.getboolean("Einweisung","enable_channel_info_on_leaving")
        if not enable_info:
            return
        info_channel = self._get_info_channel()
        if info_channel is None:
            return
        department_roles_ids = [int(role_id.strip()) for role_id in config.get("Role Management", "department1_ranks").split(",")]
        department_roles = [member.guild.get_role(role_id) for role_id in department_roles_ids]
        if any(role.id in department_roles for role in member.roles):
            embed = discord.Embed(
                title="Departmentmeber left the server.",
                description=f"{member.mention} has left the server. Name: {member.name}, {member.nick}, ID: {member.id}",
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            await info_channel.send(embed=embed)
        else:
            return

def setup(bot: discord.Bot):
    bot.add_cog(infoleaving(bot))