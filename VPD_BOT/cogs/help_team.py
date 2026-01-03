import json
from pathlib import Path
import discord
from discord.ext import commands
from discord.commands import slash_command

class helpteam(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    @slash_command(name="help_team", description="Get Infos on how to join the Team")
    async def help_team(self, ctx: discord.ApplicationContext):
        server = ctx.guild

        json_path = Path(__file__).resolve().parent / "json_files" / "help_team.json"
        if not json_path.exists():
            await ctx.respond("The help_team.json file is missing.")
            return

        try:
            with json_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            await ctx.respond("The help_team.json file is not valid JSON.")
            return

        if isinstance(json_data, dict):
            entries = [json_data]
        elif isinstance(json_data, list):
            entries = json_data
        else:
            await ctx.respond("The help_team.json file has an unexpected structure.")
            return

        if not entries or not isinstance(entries[0], dict):
            await ctx.respond("The help_team.json file has an unexpected structure.")
            return

        if not entries:
            await ctx.respond("The help_team.json file is empty.")
            return

        entry = entries[0]
        jstitle = entry.get("title", "Help Team")
        jsdesc = entry.get("desc", "No description provided.")
        
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