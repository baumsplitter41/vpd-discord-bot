import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

load_dotenv()
token = os.getenv("TOKEN")
if token is None:
    raise ValueError("TOKEN not found in .env file")

debug_guilds_up = []
server_token = os.getenv("SERVER").split(",")
for i in range(len(server_token)):
    debug_guilds_up.append(int(server_token[i]))
    
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="BaumSplitter41 Test Bot",
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

@bot.event
async def on_ready():
    print(f"{bot.user} ist online")

@bot.listen()
async def on_guild_join(guild):
    print(f"LOG: guild {guild} joined")


#---------------------------------------------------------------------------------------#
#DONT Touch anything above this line, unless you know what you are doing!#
#---------------------------------------------------------------------------------------#

#---------------------------------#
## Deleted Message
"""
@bot.event
async def on_message_delete(
    ctx = discord.Message,
):
    if ctx.author != bot.user:
        await ctx.send(f"Eine Nachricht von {ctx.author} wurde gelöscht: {ctx.content}", ephemeral=False)
"""
#---------------------------------#

#---------------------------------#
@bot.event
async def on_message_delete(msg):
    if msg.author != bot.user:  
        await msg.channel.send(f"A Message from {msg.author} has been deleted: {msg.content}")
#---------------------------------#

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
    embed.set_author(name="World Wide Modding", icon_url="https://i.lcpdfrusercontent.com/uploads/monthly_2022_04/756701490_woldwidemodding.thumb.jpg.00bc1f61c05cc6d24519e1dda202d741.jpg")
    embed.set_footer(text="World Wide Modding - Bot | Made by BaumSplitter41")

    await ctx.respond(embed=embed)
#---------------------------------#


#---------------------------------#
##Ban System

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
    
    #logging in #ban-logs on VicePD
    channel= discord.utils.get(ctx.guild.channels, id = int(1447580463668400305))

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
    embed.set_footer(text="World Wide Modding - Bot | Made by BaumSplitter41")

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














#---------------------------------#
#Run function
bot.run(token)
#---------------------------------#