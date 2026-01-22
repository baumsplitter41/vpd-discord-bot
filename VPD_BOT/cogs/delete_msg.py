import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command


class delete(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="delete", description="Delete a Number message from this server")
    async def delete(
            self,
            ctx,
            numbermsg: int = Option(int, "Select Number of the message to delete"),
        ):
        if numbermsg < 1:
            await ctx.respond("Please provide a valid number greater than 0.", ephemeral=True)
            return
        if auth := ctx.author.guild_permissions.manage_messages:
            pass
        else:
            await ctx.respond("You don't have the permission to use this command!", ephemeral=True)
            return
        deleted_messages = []
        async for msg in ctx.channel.history(limit=numbermsg + 1):
            deleted_messages.append(msg)
        if len(deleted_messages) <= 1:
            await ctx.respond("No messages found to delete.", ephemeral=True)
            return
        await ctx.channel.delete_messages(deleted_messages[1:])
        await ctx.respond(f"Deleted {len(deleted_messages) - 1} messages.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(delete(bot))