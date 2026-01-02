import discord
from discord.ext import commands
from discord.commands import slash_command

class helpteam(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(name="help_how_to_team", description="Get Infos on how to join the Team")
    async def help_how_to_team(self, ctx: discord.ApplicationContext):
        server = ctx.guild
        
        embed = discord.Embed(
            title=f"__How to join the Team on {server.name}__",
            description="If you want to join the Serverteam open a ticket in #ticket.",
            color=discord.Color.yellow()
        )

        if server.icon:
            embed.set_thumbnail(url=server.icon.url)
            
        embed.set_author(name="VicePD", icon_url="https://i.imgur.com/6QteFrg.png")
        embed.set_footer(text="VicePD - Bot | Made by BaumSplitter41")

        await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(helpteam(bot))