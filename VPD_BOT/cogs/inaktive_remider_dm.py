import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord.commands import Option
from discord.commands import slash_command
import configparser
import time
import mysql.connector


## Note: this script will be pretty hardcoded and specific for our use case. It is deactivatable in the config.cfg file.


class remiderinactive(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config

        
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_inactive_members.start()
    
    @tasks.loop(hours=48)
    async def check_inactive_members(self):
        config = self._load_config()
        enable_inavtive_reminder_dm = config.getboolean("Welcome","enable_inavtive_reminder_dm")
        if not enable_inavtive_reminder_dm:
            return # Exit the function if the feature is disabled in the config

        log_channel_id = config.getint("Logs","action_log")
        log_channel = self.bot.get_channel(log_channel_id)
    
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

        inaktive_players = []
        
        cursor.execute("""
        SELECT users.license, users.discord FROM users, players WHERE players.last_logged_out < CURDATE() - INTERVAL 14 DAY;
        """)
        for license, discord in cursor.fetchall():
            inaktive_players.append(discord)

        #Core script
        discord_ids = []
        for discord_value in inaktive_players:
            discord_raw = discord_value.split(":")
            for discord_part in discord_raw:
                if discord_part.isdigit():
                    discord_ids.append(discord_part)

        for discord_id in discord_ids:
            user_id = int(discord_id)
            user = self.bot.get_user(user_id)
            if user is not None:
                try:
                    await user.send("Hey, du warst eine ganze Weile außer Dienst – höchste Zeit, wieder einzusteigen und den Bürgern von Los Santos auf den Straßen zu helfen! 🚔")
                    await log_channel.send(f"Sent inactivity reminder DM to {user.name} ({user.id})")
                except Exception as e:
                    print(f"Could not send DM to {user.name}: {e}")
                    await log_channel.send(f"Could not send DM to {user.name} ({user.id}): {e}")
            else:
                print(f"Could not find user with ID {user_id}")
                await log_channel.send(f"Could not find user with ID {user_id}")
        
        cursor.close()
        conn.close()



def setup(bot: discord.Bot):
    bot.add_cog(remiderinactive(bot))
                            


            
        
            

    
        
    
        
    
