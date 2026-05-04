import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time
import json
from pathlib import Path

class reactionroles(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    
    def _get_roles(self):
        config = self._load_config()
        role_ids = [int(role_id.strip()) for role_id in config["Reactionroles"]["reactionroles_role_ids"].split(",")]
        roles = [self.bot.get_role(role_id) for role_id in role_ids]
        if any(role is None for role in roles):
            print(f"One or more roles with IDs {role_ids} not found.")
            return
        return roles
    def _get_emojis(self):
        config = self._load_config()
        emojis = [emoji.strip() for emoji in config["Reactionroles"]["reactionroles_emojis"].split(",")]
        return emojis
    def _get_message_id(self):
        config = self._load_config()
        message_id = int(config["Reactionroles"]["reactionroles_message_id"].strip())
        return message_id
    
    #Get the reaction role embed text from the .json file
    def _reaction_role_embed(self):
        json_path = Path(__file__).resolve().parent.parent.joinpath("json_files", "reaction_role_msg.json")
        if not json_path.exists():
            print("The .json file is missing.")
            return
        try:
            with json_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            print("The .json file is not valid JSON.")
            return
        if isinstance(json_data, dict):
            entries = [json_data]
        elif isinstance(json_data, list):
            entries = json_data
        else:
            print("The .json file has an unexpected structure.")
            return
        if not entries or not isinstance(entries[0], dict):
            print("The .json file has an unexpected structure.")
            return
        if not entries:
            print("The .json file is empty.")
            return

        entry = entries[0]
        jstitle = entry.get("title", "Reaction Roles")
        jsdesc = entry.get("desc", "No description provided.")
        
        embed = discord.Embed(
            title=f"{jstitle}",
            description=f"{jsdesc}",
            color=discord.Color.blue()
        )
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")
        return embed
    

    #Setup the reaction role message
    @slash_command(name="setup_reactionrole", description="Setup the reaction role message")
    async def reactionmsg(
            self,
            ctx,
            channel: discord.TextChannel = Option(discord.TextChannel, "Select Channel", required=True)
        ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You don't have permission to use this command.")
            return
        embed = self._reaction_role_embed()
        if embed is None:
            await ctx.respond("Failed to load the reaction role message.")
            return
        message = await channel.send(embed=embed)
        await ctx.respond(f"Reaction role message has been set up in {channel.mention}.", ephemeral=True)
        # Add reactions to the message
        emojis = self._get_emojis()
        if emojis is None:
            await ctx.respond("Failed to load emojis from config.", ephemeral=True)
            return
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                await ctx.respond(f"Failed to add reaction {emoji}: {e}", ephemeral=True)
        
        
        
#-----------------------------------------------#

    #Add role to user
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        #Get variables
        user = self.parse_reaction_payload(payload)
        if user.bot:
            return
        message_id = self._get_message_id()
        if message_id is None:
            return
        emojis = self._get_emojis()
        if emojis is None:
            return
        if payload.emoji.id not in emojis:
            return
        roles = self._get_roles()
        if roles is None:
            return
        
        #Add the role to the user
        for emoji, role in zip(emojis, roles):
            if payload.emoji.id == emoji:
                await user.add_roles(role)
                remove_reaction = discord.utils.get(guild.emojis, id=emoji)
                await payload.member.remove_reaction(remove_reaction, message_id)
                break


    #Remove role from user
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        #Get variables
        user = self.parse_reaction_payload(payload)
        if user.bot:
            return
        message_id = self._get_message_id()
        if message_id is None:
            return
        emojis = self._get_emojis()
        if emojis is None:
            return
        if payload.emoji.id not in emojis:
            return
        roles = self._get_roles()
        if roles is None:
            return
        
        #Add the role to the user
        for emoji, role in zip(emojis, roles):
            if payload.emoji.id == emoji:
                await user.remove_roles(role)
                remove_reaction = discord.utils.get(guild.emojis, id=emoji)
                await payload.member.remove_reaction(remove_reaction, message_id)
                break
        
        
def setup(bot: discord.Bot):
    bot.add_cog(reactionroles(bot))