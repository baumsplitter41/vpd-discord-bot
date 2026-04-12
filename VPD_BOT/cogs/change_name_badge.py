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
        enable_change_dc_name = config.getboolean("Role Management", "enable_change_dc_name", fallback=False)
        if not enable_change_dc_name:
            return 

        # Load .env file for the gameserver database
        load_dotenv()
        dbhost = os.getenv("HOST2")
        dbname = os.getenv("NAME2")
        dbpsswd = os.getenv("PASSWORD2")
        dbdb = os.getenv("DATABASE2")
        guild_id = os.getenv("SERVER")

        if not all([dbhost, dbname, dbpsswd, dbdb, guild_id]):
            print("Fehler: Mindestens eine .env Variable fehlt!")
            return

        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            print("Server (Guild) nicht gefunden.")
            return

        # Database initialization
        try:
            conn = mysql.connector.connect(
                host=dbhost, user=dbname, password=dbpsswd, database=dbdb,
                charset='utf8mb4', collation='utf8mb4_unicode_ci'
            )
            cursor = conn.cursor()
        except Exception as e:
            print(f"Datenbankverbindung fehlgeschlagen: {e}")
            return

        # 1. ALLES in EINER Abfrage holen (verhindert Listen-Verschiebungen)
        cursor.execute("""
            SELECT 
                ny_groups_meta.internal_identifier, 
                players.charinfo, 
                users.discord 
            FROM ny_groups_meta
            JOIN players ON ny_groups_meta.character_identifier = players.citizenid
            JOIN users ON players.userId = users.userId
            ORDER BY ny_groups_meta.internal_identifier
        """)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()

        # 2. Daten filtern und Duplikate (Twinks) aussortieren
        valid_users = {}
        blacklisted_ids = set()

        for badge, char_data, discord_str in rows:
            if not discord_str:
                continue

            # Discord ID extrahieren
            discord_id_parts = discord_str.split(":")
            user_id = None
            for part in discord_id_parts:
                if part.isdigit():
                    user_id = int(part)
                    break
            
            if not user_id:
                continue

            # --- DEIN DUPLIKAT-SCHUTZ ---
            # Wenn der User schon geblacklistet ist, überspringen
            if user_id in blacklisted_ids:
                continue 
            
            # Wenn wir den User zum ZWEITEN Mal sehen, ist es ein Duplikat
            if user_id in valid_users:
                del valid_users[user_id] # Von den gültigen löschen
                blacklisted_ids.add(user_id) # Auf die Blacklist setzen
                continue

            # Vornamen und Nachnamen aus JSON holen
            firstname, lastname = "", ""
            if char_data:
                try:
                    char_dict = json.loads(char_data)
                    firstname = char_dict.get("firstname", "")
                    lastname = char_dict.get("lastname", "")
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass 

            # Ziel-Nickname generieren und auf 32 Zeichen limitieren (Discord Limit)
            target_nick = f"[{badge}] {firstname} {lastname}".strip()
            if len(target_nick) > 32:
                target_nick = target_nick[:32]

            # User in die Liste der "sicheren" Einträge packen
            valid_users[user_id] = target_nick


        # 3. Namen auf dem Discord-Server aktualisieren
        print(f"Aktualisiere {len(valid_users)} User. Duplikate ignoriert: {len(blacklisted_ids)}")
        
        for user_id, target_nick in valid_users.items():
            member = guild.get_member(user_id)
            if member:
                # WICHTIG: Nur ändern, wenn der Name nicht schon exakt so ist! (Schützt vor Discord API Sperren)
                if member.display_name != target_nick:
                    try:
                        await member.edit(nick=target_nick)
                    except discord.Forbidden:
                        pass # Der Bot hat nicht die Rechte (User hat höhere Rolle als der Bot)
                    except Exception as e:
                        print(f"Fehler beim Ändern des Namens von User {user_id}: {e}")

def setup(bot: discord.Bot):
    bot.add_cog(changedcname(bot))
