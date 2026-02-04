import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time


class actionlog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    
#Delted Message Log
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)
        if message.author.bot:
            return
        else:
            embed = discord.Embed(
                title="Message Deleted",
                description=f"A message by {message.author.mention} was deleted in {message.channel.mention}.",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            embed.add_field(name="Message Content", value=message.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")
            await log_channel.send(embed=embed)

#Edited Message Log
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)
        if before.author.bot:
            return
        else:
            embed = discord.Embed(
                title="Message Edited",
                description=f"A message by {before.author.mention} was edited in {before.channel.mention}.",
                color=discord.Color.orange(),
                timestamp=after.edited_at or discord.utils.utcnow()
            )
            embed.add_field(name="Before", value=before.content or "No content", inline=False)
            embed.add_field(name="After", value=after.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {before.author.id} | Message ID: {before.id}")
            await log_channel.send(embed=embed)

#Member Join Log
    @commands.Cog.listener()
    async def on_member_join(self, member):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} has joined the server.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"User ID: {member.id}")
        await log_channel.send(embed=embed)

#Member Leave Log
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} has left the server.",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"User ID: {member.id}")
        await log_channel.send(embed=embed)


#Role Update Log
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Role Updated",
            description=f"The role **{before.name}** has been updated.",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Before", value=f"Name: {before.name}\nColor: {before.color}\nPermissions: {before.permissions}", inline=False)
        embed.add_field(name="After", value=f"Name: {after.name}\nColor: {after.color}\nPermissions: {after.permissions}", inline=False)
        embed.set_footer(text=f"Role ID: {before.id}")
        await log_channel.send(embed=embed)

#Role added log

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Role Created",
            description=f"The role **{role.name}** has been created.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Role ID: {role.id}")
        await log_channel.send(embed=embed)

#Role deleted log

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        embed = discord.Embed(
            title="Role Deleted",
            description=f"The role **{role.name}** has been deleted.",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Role ID: {role.id}")
        await log_channel.send(embed=embed)


#User Role update log
    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        config = self._load_config()
        enable_log = config.getboolean("Logs","enable_action_log")  
        if not enable_log:
            return
        log_channel_id = int(config["Logs"]["action_log"])
        log_channel = self.bot.get_channel(log_channel_id)

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        for role in added_roles:
            embed = discord.Embed(
                title="Role Added",
                description=f"The role **{role.name}** has been added to {after.mention}.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"User ID: {after.id} | Role ID: {role.id}")
            await log_channel.send(embed=embed)

        for role in removed_roles:
            embed = discord.Embed(
                title="Role Removed",
                description=f"The role **{role.name}** has been removed from {after.mention}.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"User ID: {after.id} | Role ID: {role.id}")
            await log_channel.send(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(actionlog(bot))