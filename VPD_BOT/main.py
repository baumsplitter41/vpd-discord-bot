import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
from datetime import datetime
import configparser
import mysql.connector


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)
#---------------------------------#
#Load .env file

load_dotenv()
token = os.getenv("TOKEN")
if token is None:
    raise ValueError("TOKEN not found in .env file")

debug_guilds_up = []
server_token = os.getenv("SERVER").split(",")
for i in range(len(server_token)):
    debug_guilds_up.append(int(server_token[i]))

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

#---------------------------------#
#ConfigParser

config = configparser.RawConfigParser()
configFilePath = r'config.cfg'
config.read_file(open(configFilePath))

label_rules = config.get('Reactionroles Rules', 'label_rules')
role_rules = config.get('Reactionroles Rules', 'rules_role')

channel_log = config.get('Logs', 'channel_log')
channel_banlog = config.get('Logs', 'ban_log')

#---------------------------------#
#Database initialization
conn = mysql.connector.connect(
    host=dbhost,
    user=dbname,
    password=dbpsswd
)
cursor = conn.cursor()
conn.database = dbdb

cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid BIGINT,
    discordname VARCHAR(100),
    roles INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Warns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid BIGINT,
    username VARCHAR(100),
    moderatorname VARCHAR(100),
    reason VARCHAR(250),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Bans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid BIGINT,
    username VARCHAR(100),
    moderatorname VARCHAR(100),
    reason VARCHAR(250),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Unbans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid BIGINT,
    username VARCHAR(100),
    moderatorname VARCHAR(100),
    reason VARCHAR(250),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

cursor.execute("""
CREATE TABLE IF NOT EXISTS Kick (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid BIGINT,
    username VARCHAR(100),
    moderatorname VARCHAR(100),
    reason VARCHAR(250),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


#---------------------------------#
#Initialize Bot

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="VicePD Bot",
    intents=intents,
    debug_guilds=debug_guilds_up if debug_guilds_up else None
)

#Loading Cogs
def load_extensions():
    cogs_dir = "./cogs"
    if not os.path.exists(cogs_dir):
        print(f"Cogs directory '{cogs_dir}' not found!")
        return
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            cog_list = os.path.splitext(filename)[0]
            try:
                bot.load_extension(f"cogs.{cog_list}")
                print(f"Loaded cog: {cog_list}")
            except Exception as e:
                print(f"Failed to load cog {cog_list}: {e}")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


#---------------------------------#
#Print in Log if error occurs
@bot.event
async def on_application_command_error(ctx, error):
    channel = discord.utils.get(ctx.guild.channels, id=int(channel_log))
    if channel:
        await channel.send(f"Error occurred: {str(error)}")

#---------------------------------#
#Bot Online Console
@bot.event
async def on_ready():
    print(f"{bot.user} is online")
    if bot.guilds:
        channel = discord.utils.get(bot.guilds[0].channels, id=int(channel_log))
        if channel:
            await channel.send(f"{bot.user} is online")
    bot.add_view(PersistentRoleView()) #loading reactionrole memory
    print("Registrierte Slash-Commands:")
    for command in bot.pending_application_commands:
        print(f" - {command.name}")
        await channel.semd(f"- {command.name}")

#---------------------------------------------------------------------------------------#
#DONT Touch anything above this line, unless you know what you are doing!#
#---------------------------------------------------------------------------------------#

#_________________________________#
#BAN SYSTEM
#---------------------------------#
##Ban
@bot.slash_command(name="ban", description="Ban a user from this Server")
async def ban(
    ctx,
    user: Option(discord.User, description = "Select User", required=True), # type: ignore
    reason: Option(str, description = "Reason for the ban", default="No reason provided") # type: ignore
    
):
    if not ctx.author.guild_permissions.ban_members:
        await ctx.respond("Error: You don't have the permission to ban Members!", ephemeral=True)
        return
    
    if user == bot.user:
        await ctx.respond("Error: I can't ban myself!", ephemeral=True)
        return
    if user == ctx.author:
        await ctx.respond("Error: You can't ban yourself!", ephemeral=True)
        return
    
    channel= discord.utils.get(ctx.guild.channels, id = int(channel_banlog))

    embed = discord.Embed(
        title=f"Ban of **{user.name}**",
        description=f"User {user.mention} has been banned from the Server",
        color=discord.Color.red()
    )
    time = discord.utils.format_dt(datetime.now(), "f")
    embed.add_field(name="Ban Date", value=time, inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.add_field(name="User ID", value=user.id)

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
    embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

    try:
        await ctx.guild.ban(user, reason=reason)
        await ctx.respond(f"User {user.mention} has been banned from this Server!", ephemeral=True)
        await channel.send(embed=embed)
        cursor.execute(
            "INSERT INTO Bans (userid, username, moderatorname, reason) VALUES (%s, %s, %s, %s)",
            (user.id, str(user), str(ctx.author), reason)
        )
        conn.commit()

    except discord.Forbidden:
        await ctx.respond("Error: I don't have permission to ban this user.", ephemeral=True)
    except discord.HTTPException as e:
        await ctx.respond(f"Error: Could not ban User {user.mention}. Reason: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Unexpected error: {e}", ephemeral=True)

#---------------------------------#
#Unban
@bot.slash_command(name="unban", description="Unban a user from this Server")
async def unban(
    ctx,
    user: Option(discord.User, description = "Insert User ID", required=True), # type: ignore
    reason: Option(str, description = "Reason for the unbanning", default="No reason provided") # type: ignore
    
):
    if not ctx.author.guild_permissions.ban_members:
        await ctx.respond("Error: You don't have the permission to unban Members!", ephemeral=True)
        return
    
    if user == bot.user:
        await ctx.respond("Error: I can't unban myself!", ephemeral=True)
        return
    if user == ctx.author:
        await ctx.respond("Error: You can't unban yourself!", ephemeral=True)
        return
    if user in ctx.guild.members:
        await ctx.respond("Error: This user is not banned!", ephemeral=True)
        return
    
    channel= discord.utils.get(ctx.guild.channels, id = int(channel_banlog))

    embed = discord.Embed(
        title=f"Unban of **{user.name}**",
        description=f"User {user.mention} was unbanned from this server.",
        color=discord.Color.green()
    )
    time = discord.utils.format_dt(datetime.now(), "f")
    embed.add_field(name="Unban Date", value=time, inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.add_field(name="User ID", value=user.id)

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
    embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

    try:
        await ctx.guild.unban(user, reason=reason)
        await ctx.respond(f"User {user.mention} is now unbanned!", ephemeral=True)
        await channel.send(embed=embed)
        cursor.execute(
            "INSERT INTO Unbans (userid, username, moderatorname, reason) VALUES (%s, %s, %s, %s)",
            (user.id, str(user), str(ctx.author), reason)
        )
        conn.commit()

    except discord.Forbidden:
        await ctx.respond("Error: I don't have permission to unban this user.", ephemeral=True)
    except discord.HTTPException as e:
        await ctx.respond(f"Error: Could not unban User {user.mention}. Reason: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Unexpected error: {e}", ephemeral=True)

#---------------------------------#
#_________________________________#


#---------------------------------#
#Kick
@bot.slash_command(name="kick", description="Kick a user from this Server")
async def kick(
    ctx,
    user: Option(discord.User, description = "Select User", required=True), # type: ignore
    reason: Option(str, description = "Reason for the ban", default="No reason provided") # type: ignore
    
):
    if not ctx.author.guild_permissions.kick_members:
        await ctx.respond("Error: You don't have the permission to kick Members!", ephemeral=True)
        return
    
    if user == bot.user:
        await ctx.respond("Error: I can't kick myself!", ephemeral=True)
        return
    if user == ctx.author:
        await ctx.respond("Error: You can't kick yourself!", ephemeral=True)
        return
    
    channel= discord.utils.get(ctx.guild.channels, id = int(channel_banlog))

    embed = discord.Embed(
        title=f"Kick of **{user.name}**",
        description=f"User {user.mention} has been kicked from the Server",
        color=discord.Color.red()
    )
    time = discord.utils.format_dt(datetime.now(), "f")
    embed.add_field(name="Kick Date", value=time, inline=False)
    embed.add_field(name="Moderator", value=f"{ctx.author}", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.add_field(name="User ID", value=user.id)

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
    embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")


    try:
        await ctx.guild.kick(user, reason=reason)
        await ctx.respond(f"User {user.mention} has been kicked from this Server!", ephemeral=True)
        cursor.execute(
            "INSERT INTO Kick (userid, username, moderatorname, reason) VALUES (%s, %s, %s, %s)",
            (int(user.id), str(user), str(ctx.author), reason)
        )
        conn.commit()
        await channel.send(embed=embed)


    except discord.Forbidden:
        await ctx.respond("Error: I don't have permission to kick this user.", ephemeral=True)
    except discord.HTTPException as e:
        await ctx.respond(f"Error: Could not kick User {user.mention}. Reason: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Unexpected error: {e}", ephemeral=True)

#---------------------------------#

#---------------------------------#
#Warn
@bot.slash_command(name="warn", description="Warn a user from this Server")
async def warn(
    ctx,
    user: Option(discord.User, required=True), # type: ignore
    reason: Option(str, default="No reason provided") # type: ignore
):
    await ctx.defer(ephemeral=True)

    if not ctx.author.guild_permissions.kick_members:
        await ctx.followup.send("No permission.", ephemeral=True)
        return

    if user in (bot.user, ctx.author):
        await ctx.followup.send("Invalid target.", ephemeral=True)
        return

    cursor.execute(
        "INSERT INTO Warns (userid, username, moderatorname, reason) VALUES (%s, %s, %s, %s)",
        (user.id, str(user), str(ctx.author), reason)
    )
    conn.commit()

    await ctx.followup.send(
        f"User {user.mention} has been warned for: {reason}",
        ephemeral=True
    )

#---------------------------------#
#Modinfo
@bot.slash_command(name="modinfo", description="Shows the moderative history of a user from this Server")
async def modinfo(
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

    cursor.execute(
        "SELECT moderatorname, reason, date FROM Warns WHERE userid = %s",
        (user.id,)
    )
    warns = cursor.fetchall()
    if warns:
        for moderatorname, reason, date in warns:
            embed.add_field(
                name=f"Warned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                value=f"Reason: {reason}",
                inline=False
            )

    cursor.execute(
        "SELECT moderatorname, reason, date FROM Kick WHERE userid = %s",
        (user.id,)
    )
    kicks = cursor.fetchall()
    if kicks:
        for moderatorname, reason, date in kicks:
            embed.add_field(
                name=f"Kicked by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                value=f"Reason: {reason}",
                inline=False
            )

    cursor.execute(
        "SELECT moderatorname, reason, date FROM Bans WHERE userid = %s",
        (user.id,)
    )
    bans = cursor.fetchall()
    if bans:
        for moderatorname, reason, date in bans:
            embed.add_field(
                name=f"Banned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                value=f"Reason: {reason}",
                inline=False
            )

    cursor.execute(
        "SELECT moderatorname, reason, date FROM Unbans WHERE userid = %s",
        (user.id,)
    )
    unbans = cursor.fetchall()
    if unbans:
        for moderatorname, reason, date in unbans:
            embed.add_field(
                name=f"Unbanned by {moderatorname} on {date.strftime('%Y-%m-%d %H:%M:%S')}",
                value=f"Reason: {reason}",
                inline=False
            )

    if not warns and not kicks and not bans and not unbans:
        await ctx.followup.send(f"User {user.mention} has no moderation history.", ephemeral=True)
        return

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
    embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

    await ctx.followup.send(embed=embed, ephemeral=False)


#_________________________________#
## Reaction role system

#---------------------------------#
#reaction role verfiy

class PersistentRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label=label_rules, 
        style=discord.ButtonStyle.success, 
        emoji="✅", 
        custom_id="persistent_view:role_verify" 
    )
    async def verify_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(role_rules))
        
        if role is None:
            await interaction.response.send_message("Error: The konfigured role was not found", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Rolle **{role.name}** wurde entfernt.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Du hast die Rolle **{role.name}** erhalten!", ephemeral=True)



@bot.slash_command(name="verify_message", description="Send the reactionrole message")
async def setup_rr(
    ctx: discord.ApplicationContext,
    channel: discord.TextChannel, 
    title: str,
    description: str
):

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You dont have the permissions to do that..", ephemeral=True)
        return

    embed = discord.Embed(
        title=title,
        description=f"{description}\n\nViel Spass auf dem Server!",
        color=discord.Color.red()
    )
    embed.set_image(url="https://i.imgur.com/FoF791J.png")

    try:
        await channel.send(embed=embed, view=PersistentRoleView())
        await ctx.respond(f"Message was succesfully sent in {channel.mention}!", ephemeral=True)
    except discord.Forbidden:
        await ctx.respond("I dont have permissions to write in this channel", ephemeral=True)
#---------------------------------#
#_________________________________#


#---------------------------------#
#Run function
load_extensions()
bot.run(token)
#---------------------------------#