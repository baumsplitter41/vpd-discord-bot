import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time
import mysql.connector
import json



## Note: to use this script on a other server you need to change the SQL querys. It is deactivatable in the config.cfg file.


class changedcname(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config

        
    @commands.Cog.listener()
    async def on_ready(self):
        self.change_name_badge.start()
    
    @tasks.loop(minutes=15)
    async def change_name_badge(self):
        config = self._load_config()
        enable_change_dc_name = config.getboolean("Role Management","enable_change_dc_name")
        if not enable_change_dc_name:
            return # Exit the function if the feature is disabled in the config


    #Load .env file for the gameserver database
        dbhost = os.getenv("HOST2")
        if dbhost is None:
            raise ValueError("HOST2 not found in .env file")
        dbname = os.getenv("NAME2")
        if dbname is None:
            raise ValueError("NAME2 not found in .env file")
        dbpsswd = os.getenv("PASSWORD2")
        if dbpsswd is None:
            raise ValueError("PASSWORD2 not found in .env file")
        dbdb = os.getenv("DATABASE2")
        if dbdb is None:
            raise ValueError("DATABASE2 not found in .env file")
        
        #Get guild ID
        load_dotenv()
        guild_id = os.getenv("SERVER")
        if guild_id is None:
            raise ValueError("SERVER not found in .env file")
        

        #Database initialization
        conn = mysql.connector.connect(
            host=dbhost,
            user=dbname,
            password=dbpsswd,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        cursor = conn.cursor()
        conn.database = dbdb


        #needed arrays
        badgenr = []
        charinfo = []
        users = []
        discord_raw = []
        firstname = []
        lastname = []
        
        #get information from database
        cursor.execute("""
        SELECT ny_groups_meta.internal_identifier FROM ny_groups_meta, 
        users, players WHERE ny_groups_meta.character_identifier=players.citizenid AND 
        players.userId=users.userId
        """)
        for internal_identifier in cursor.fetchall():
            badgenr.append(internal_identifier[0])
        
        cursor.execute("""
        SELECT players.charinfo FROM ny_groups_meta, 
        users, players WHERE ny_groups_meta.character_identifier=players.citizenid AND 
        players.userId=users.userId
        """)
        for char_info in cursor.fetchall():
            charinfo.append(char_info[0])
        
        cursor.execute("""
        SELECT users.discord FROM ny_groups_meta, 
        users, players WHERE ny_groups_meta.character_identifier=players.citizenid AND 
        players.userId=users.userId
        """)
        for discord in cursor.fetchall():
            discord_raw.append((discord))
        

        #get users to the discordIDs
        for discord in discord_raw:
            discord_id = discord[0].split(":")
            for i in range(len(discord_id)):
                if discord_id[i].isdigit():
                    user_id = int(discord_id[i])
                    user = self.bot.get_user(user_id)
                    users.append(user)
                    break
        

        # check on duplicates
        unique_users = []
        unique_badgenr = []
        unique_charinfo = []
        seen_user_ids = set()
        ignored_duplicates = set()  # To track and ignore duplicate users

        for user, badge, cinfo in zip(users, badgenr, charinfo):
            if user is None:
                continue 

            if user.id in seen_user_ids:
                print(f"Duplicate user found: {user.name} (ID: {user.id})")
                ignored_duplicates.add(user.id)  # Add to ignored duplicates
                ignored_duplicates.add(user.badge)
                ignored_duplicates.add(user.cinfo)
                continue

            seen_user_ids.add(user.id)
            unique_users.append(user)
            unique_badgenr.append(badge)
            unique_charinfo.append(cinfo)

        users = unique_users
        badgenr = unique_badgenr
        charinfo = unique_charinfo

        #get charname
        for char_data in charinfo:
            try:
                char_dict = json.loads(char_data)
                firstname.append(char_dict.get("firstname", ""))
                lastname.append(char_dict.get("lastname", ""))
            except (json.JSONDecodeError, KeyError, TypeError):
                firstname.append("")
                lastname.append("")


        #change username        
        for user, badge, first, last in zip(users, badgenr, firstname, lastname):
            nick = f"[{badge}] {first} {last}"
            try:
                guild = self.bot.get_guild(int(guild_id))
                member = guild.get_member(user.id)
                if member:
                    await member.edit(nick=nick)
            except Exception as e:
                print(f"Failed to change nickname for {user.name}: {e}")

      
        cursor.close()
        conn.close()



def setup(bot: discord.Bot):
    bot.add_cog(changedcname(bot))
