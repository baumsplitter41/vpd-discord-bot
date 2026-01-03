import json
import os
import discord
from discord.ext import commands
from discord.commands import slash_command

class helpteam(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    @slash_command(name="help_how_to_team", description="Get Infos on how to join the Team")
    async def help_how_to_team(self, ctx: discord.ApplicationContext):
        server = ctx.guild

        #Loading the JSON file
        JSON_FILE_PATH = 'cogs/json_files/help_team.json'
        if not os.path.exists(JSON_FILE_PATH):
            await ctx.respond("The help_team.json file is missing.")
            return
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        for entry in json_data:
            jstitle = entry.get("title", "")
            jsdesc = entry.get("desc", "")



        
        embed = discord.Embed(
            title=f"{jstitle}",
            description=f"{jsdesc}",
            color=discord.Color.yellow()
        )

        if server.icon:
            embed.set_thumbnail(url=server.icon.url)
            
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(helpteam(bot))