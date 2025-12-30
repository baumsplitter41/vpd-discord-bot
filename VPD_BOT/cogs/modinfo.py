import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv
import mysql.connector
import configparser


#Bot initialization
class greet(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        #---------------------------------#
        #ENV initialization
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

        #Database initialization
        conn = mysql.connector.connect(
            host=dbhost,
            user=dbname,
            password=dbpsswd
        )
        self.cursor = conn.cursor()
        conn.database = dbdb



#Command initialization
    @slash_command(name="modinfo", description="Shows the moderative history of a user from this Server")
    async def modinfo(
        self,
        ctx,
        user: Option(discord.User, required=True) # type: ignore
    ):
        await ctx.defer(ephemeral=False)

        if not ctx.author.guild_permissions.kick_members:
            await ctx.followup.send("No permission.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"__Moderation History for {user.name}__",
            color=discord.Color.orange()
        )

        self.cursor.execute(
            "SELECT moderatorname, reason, date FROM Warns WHERE userid = %s",
            (user.id,)
        )
        warns = self.cursor.fetchall()
        if warns:
            for moderatorname, reason, date in warns:
                embed.add_field(
                    name=f"Warned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Reason: {reason}",
                    inline=False
                )

        self.cursor.execute(
            "SELECT moderatorname, reason, date FROM Kick WHERE userid = %s",
            (user.id,)
        )
        kicks = self.cursor.fetchall()
        if kicks:
            for moderatorname, reason, date in kicks:
                embed.add_field(
                    name=f"Kicked by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Reason: {reason}",
                    inline=False
                )

        self.cursor.execute(
            "SELECT moderatorname, reason, date FROM Bans WHERE userid = %s",
            (user.id,)
        )
        bans = self.cursor.fetchall()
        if bans:
            for moderatorname, reason, date in bans:
                embed.add_field(
                    name=f"Banned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Reason: {reason}",
                    inline=False
                )

        self.cursor.execute(
            "SELECT moderatorname, reason, date FROM Unbans WHERE userid = %s",
            (user.id,)
        )
        unbans = self.cursor.fetchall()
        if unbans:
            for moderatorname, reason, date in unbans:
                embed.add_field(
                    name=f"Unbanned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Reason: {reason}",
                    inline=False
                )

        if not warns and not kicks and not bans and not unbans:
            await ctx.followup.send(f"User `{user.name}` has no moderation history.", ephemeral=True)
            return

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.followup.send(embed=embed, ephemeral=False)



def setup(bot: discord.Bot):
    bot.add_cog(greet(bot))
