import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import os
from dotenv import load_dotenv

class howtostart(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="how_to_start", description= "Get Infos")
    async def how_to_start(
        self,
        ctx,
    ):
        server = ctx.guild
        embed = discord.Embed(
            title=f"__How to start__",
            description=f"Hallo {ctx.author.mention}, um auf unserem Server spielen zu können, ließ dir zuerst das Regelwerk in in #regelwerk durch. Um einem Department beizutreten wähle in #how-to-start eine Einweisungsrolle aus. Melde dich anschließend für eine Einweisung an. **Wichtig: gehe erst krz vor der Einweisung auf den Server!**",
            color=discord.Color.yellow()
        )


        embed.set_thumbnail(url=server.icon)
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(howtostart(bot))
