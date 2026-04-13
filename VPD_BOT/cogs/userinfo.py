import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import mysql.connector
import configparser
import os
from dotenv import load_dotenv



class userinfo(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    
    def _connect_db(self):
        load_dotenv()
        dbhost = os.getenv("HOST")
        if dbhost is None:
            raise ValueError("HOST not found in .env file")
        dbname = os.getenv("NAME")
        if dbname is None:
            raise ValueError("NAME not found in .env file")
        dbpsswd = os.getenv("PASSWORD")
        if dbpsswd is None:
            raise ValueError("PASSWORD not found in .env file")
        dbdb = os.getenv("DATABASE")
        if dbdb is None:
            raise ValueError("DATABASE not found in .env file")

        connection = mysql.connector.connect(
            host=dbhost,
            user=dbname,
            password=dbpsswd,
            database=dbdb
        )
        return connection


#Command initialization
    @slash_command(name="userinfo", description="Show informations of a user from this server")
    async def userinfo(
            self,
            ctx,
            user: str = Option(discord.User, "Select User"),
        ):

        config = self._load_config()
        team_role_id = config.get('Team Roles', 'team_role_id')
        team_role = ctx.guild.get_role(int(team_role_id))
        conn = self._connect_db()
        cursor = conn.cursor()
        conn.database = self._connect_db().database

        if team_role not in ctx.author.roles:
            await ctx.respond("You don't have the permission to use this command!", ephemeral=True)
            return

        if user is None:
            user = ctx.author
        elif user not in ctx.guild.members:
            await ctx.respond("The selected user is not a member on this Server!", ephemeral=True)
            return
        elif user == self.bot.user:
            await ctx.respond(f"This is me - the {self.bot.user}", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Information about *{user.name}*",
            description=f"Here you see all details about {user.mention}",
            color=discord.Color.blue()
        )

        #get database entrys of the notes
        events = []
        cursor.execute("SELECT moderatorname, information, date FROM Notes WHERE userid = %s", (user.id,))
        for moderatorname, reason, date in cursor.fetchall():
            events.append((moderatorname, reason, date))


        time = discord.utils.format_dt(user.created_at, "R")

        embed.add_field(name="Account creation date", value=time, inline=False)
        if len(user.roles) >= 2:
            embed.add_field(name="Roles", value=", ".join([role.mention for role in user.roles if role.name != "@everyone"]), inline=False)
        else:
            embed.add_field(name="Roles", value="User has no roles", inline=False)
        embed.add_field(name="Server join date", value=discord.utils.format_dt(user.joined_at, "R"), inline=False)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No")
        if events:  
            for moderatorname, reason, date in events:
                embed.add_field(name=f"Note by {moderatorname} on {date}", value=reason, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(userinfo(bot))
