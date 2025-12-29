import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command


class userinfo(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="userinfo", description="Show informations of a user from this server")
    async def userinfo(
            self,
            ctx,
            user: str = Option(discord.User, "Select User"),
        ):
        if user is None:
            user = ctx.author
        elif user not in ctx.guild.members:
            await ctx.respond("The selected user is not a member on this Server!", ephemeral=True)
            return
        elif user == self.bot.user:
            await ctx.respond(f"This is me - the {self.bot.user}", ephemeral=True)
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



def setup(bot: discord.Bot):
    bot.add_cog(userinfo(bot))
