import json
from pathlib import Path
import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command

class helpstart(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="help_start", description= "Get Infos how to start playing on the server")
    async def help_start(self,ctx: discord.ApplicationContext,
    ):
        server = ctx.guild

        json_path = Path(__file__).resolve().parent.parent.joinpath("json_files", "help_start.json")
        if not json_path.exists():
            await ctx.respond("The .json file is missing.")
            return

        try:
            with json_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            await ctx.respond("The .json file is not valid JSON.")
            return

        if isinstance(json_data, dict):
            entries = [json_data]
        elif isinstance(json_data, list):
            entries = json_data
        else:
            await ctx.respond("The .json file has an unexpected structure.")
            return

        if not entries or not isinstance(entries[0], dict):
            await ctx.respond("The .json file has an unexpected structure.")
            return

        if not entries:
            await ctx.respond("The .json file is empty.")
            return

        entry = entries[0]
        jstitle = entry.get("title", "Help")
        jsdesc = entry.get("desc", "No description provided.")
        
        embed = discord.Embed(
            title=f"{jstitle}",
            description=f"{jsdesc}",
            color=discord.Color.yellow()
        )


        embed.set_thumbnail(url=server.icon)
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(helpstart(bot))
