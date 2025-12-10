import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
from datetime import datetime
import configparser


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)
#------#
#Load .env file

load_dotenv()
token = os.getenv("TOKEN")
if token is None:
    raise ValueError("TOKEN not found in .env file")

debug_guilds_up = []
server_token = os.getenv("SERVER").split(",")
for i in range(len(server_token)):
    debug_guilds_up.append(int(server_token[i]))


#------#
#ConfigParser

config = configparser.RawConfigParser()
configFilePath = r'Pycord/VPD_BOT/config.cfg'
config.read_file(open(configFilePath))

title_rules = config.get('Reactionroles Rules', 'tile_rules')
role_rules = config.get('Reactionroles Rules', 'rules_role')
channel_rules = config.get('Reactionroles Rules', 'channel_rules')
message_rules = config.get('Reactionroles Rules', 'message_rules')
emoji_rules = config.get('Reactionroles Rules', 'rules_emoji')


channel_log = config.get('Logs', 'channel_log')
channel_banlog = config.get('Logs', 'ban_log')




#------#
#Initialize Bot

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="VicePD Bot",
    intents=intents,
    debug_guilds=debug_guilds_up if debug_guilds_up else None
)

async def load_extensions():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")   



class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


#---------------------------------#
#Bot Online Console

@bot.event
async def on_ready():
    print(f"{bot.user} ist online")
    if bot.guilds:
        channel = discord.utils.get(bot.guilds[0].channels, id=int(channel_log))
        if channel:
            await channel.send(f"{bot.user} ist online")
    await load_extensions()
#---------------------------------------------------------------------------------------#
#DONT Touch anything above this line, unless you know what you are doing!#
#---------------------------------------------------------------------------------------#

#---------------------------------#
## Greet
@bot.slash_command(description="Greet a User")
async def greet(ctx, user: str = Option(discord.User, "The user, you want to greet")):
    await ctx.respond(f"Hello {user.mention}")
#---------------------------------#

#---------------------------------#
## Say
@bot.slash_command(description="Let the bot send a message")
async def say(
        ctx,
        text: str = Option(description="Input the text you want to send"),
        channel_input: discord.TextChannel = Option(description="Select the channel,where you want to send the message.")
):  
    channel= discord.utils.get(ctx.guild.channels, id = int(channel_input[2:-1]))
    await channel.send(text)
    await ctx.respond("Message sent", ephemeral=True)
#---------------------------------#

#---------------------------------#
## Userinfo
@bot.slash_command(name="userinfo", description="Show informations of a user from this server")
async def userinfo(
        ctx,
        user: str = Option(discord.User, "Select User"),
    ):
    if user is None:
        user = ctx.author
    elif user not in ctx.guild.members:
        await ctx.respond("The selected user is not a member on this Server!", ephemeral=True)
        return
    elif user == bot.user:
        await ctx.respond(f"This is me - the {bot.user}", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"Information about *{user.name}*",
        description=f"Here you see all details about {user.mention}",
        color=discord.Color.blue()
    )

    time = discord.utils.format_dt(user.created_at, "R")

    embed.add_field(name="Account creation date", value=time, inline=False)
    if len(user.roles) >= 2:
        embed.add_field(name="Roles", value=", ".join([role.mention for role in user.roles if role.name != "@everyone"]), inline=False)
    else:
        embed.add_field(name="Roles", value="User has no roles", inline=False)
    embed.add_field(name="Server join date", value=discord.utils.format_dt(user.joined_at, "R"), inline=False)
    embed.add_field(name="User ID", value=user.id)

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
    embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

    await ctx.respond(embed=embed)
#---------------------------------#


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

    except discord.Forbidden:
        await ctx.respond("Error: I don't have permission to ban this user.", ephemeral=True)
    except discord.HTTPException as e:
        await ctx.respond(f"Error: Could not ban User {user.mention}. Reason: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Unexpected error: {e}", ephemeral=True)

#---------------------------------#
#Unban
@bot.slash_command(name="unban", description="Unban a user from this Server")
async def ban(
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
async def ban(
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
    

    try:
        await ctx.guild.kick(user, reason=reason)
        await ctx.respond(f"User {user.mention} has been kick from this Server!", ephemeral=True)

    except discord.Forbidden:
        await ctx.respond("Error: I don't have permission to kick this user.", ephemeral=True)
    except discord.HTTPException as e:
        await ctx.respond(f"Error: Could not kick User {user.mention}. Reason: {e}", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Unexpected error: {e}", ephemeral=True)

#---------------------------------#
#reaction role system
"""@bot.slash_command(name="reaction_role", description="React to verify yourself and get the role")
async def reaction_role(ctx):
    role= discord.utils.get(ctx.guild.roles, id = int(role_rules))
    embed = discord.Embed(
        title= title_rules,
        description=f"React to accept the rules and get the {role} role.",
        color=discord.Color.red()
    )
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: You don't have the permission to do that!", ephemeral=True)
        return
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction("✅")
    await ctx.respond("Message sent", ephemeral=True)"""

#------------------------------------------------------------#
@bot.event
async def on_raw_reaction_add(payload):
    """
    Wird ausgeführt, wenn eine Reaktion hinzugefügt wird.
    """
    # 1. Prüfen, ob die Reaktion auf die richtige Nachricht gesetzt wurde
    if payload.message_id != message_rules:
        return

    # 2. Prüfen, ob es das richtige Emoji ist
    if str(payload.emoji) != emoji_rules:
        return

    # 4. Das Member (User) Objekt holen
    # payload.member ist in 'on_raw_reaction_add' verfügbar
    member = payload.member
    if member is None:
        return
    
    # Ignorieren, wenn der Bot selbst reagiert (optional, aber gute Praxis)
    if member.bot:
        return

    # 5. Die Rolle holen
    role = payload.guild.get_role(role_rules)
    if role is None:
        print(f"Fehler: Rolle mit ID {role_rules} wurde nicht gefunden.")
        return

    # 6. Rolle vergeben
    try:
        await member.add_roles(role)
        print(f"Rolle '{role.name}' an {member.name} vergeben.")
        
        # Optional: User per DM benachrichtigen
        # await member.send(f"Du hast die Rolle **{role.name}** erhalten!")
        
    except discord.Forbidden:
        print("Fehler: Der Bot hat keine Berechtigung, Rollen zu verwalten (Manage Roles fehlt oder Rolle ist zu hoch).")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")



#---------------------------------#
#rules message
@bot.slash_command(name="message_rules", description = "DONT USE!!")
async def message_rules(
    ctx,
):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: You don't have the permission to do that!", ephemeral=True)
        return
    role= discord.utils.get(ctx.guild.roles, id = int(role_rules))
    embed = discord.Embed(
        title= title_rules,
        description=f"React to accept the rules and get the {role} role.",
        color=discord.Color.red()
    )
    channel= discord.utils.get(ctx.guild.channels, id = int(channel_rules))
    await channel.send(embed=embed)
    await ctx.respond("Message sent", ephemeral=True)

#---------------------------------#
#Run function
bot.run(token)
#---------------------------------#