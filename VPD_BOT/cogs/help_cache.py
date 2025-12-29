import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv

class helpcache(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="help_cache", description= "Get Infos")
    async def help_cache(
        self,
        ctx,
    ):
        server = ctx.guild
        embed = discord.Embed(
            title=f"__How to clear your game cache__",
            description=f"Follow the follwing steps to clear your game cache:",
            color=discord.Color.yellow()
        )

        embed.add_field(name="Close Game", value="Close FiveM completely", inline=False)
        embed.add_field(name="Press keys", value="Win + R", inline=False)
        embed.add_field(name="Go to the folder", value="\Local\FiveM\FiveM.app\data", inline=False)
        embed.add_field(name="Delete the folders", value="cache, server-cache, server-cache-priv", inline=False)
        embed.add_field(name="Restart Game", value="Restart the game and download the resources again.", inline=False)


        embed.set_thumbnail(url=server.icon)
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(helpcache(bot))
