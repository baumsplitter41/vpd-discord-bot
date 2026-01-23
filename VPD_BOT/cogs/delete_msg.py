import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command


class delete(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="delete", description="Delete a amount messages from this server")
    async def delete(
            self,
            ctx,
            amount: int = Option(int, "Select the amount of the messages to delete", required=True),
        ):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("You don't have the permission to use this command!", ephemeral=True)
            return
        else:
            if amount is None or amount <= 0:
                await ctx.respond("Please provide a valid number greater than 0.", ephemeral=True)
                return
            elif amount > 100:
                await ctx.respond("You can only delete up to 100 messages at a time.", ephemeral=True)
                return
            deleted_messages = []
            async for msg in ctx.channel.history(limit=amount):
                deleted_messages.append(msg)
            if len(deleted_messages) == 0:
                await ctx.respond("No messages found to delete.", ephemeral=True)
                return
            await ctx.channel.delete_messages(deleted_messages)
            await ctx.respond(f"Deleted {len(deleted_messages)} messages.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(delete(bot))