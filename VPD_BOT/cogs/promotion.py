import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class promotion(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="promotion", description= "Promote a department member   to the next rank")
    async def promotion(
        self,
        ctx,
        user: str = Option(discord.User, "Select User", required=True),
    ):
        if user not in ctx.guild.members:
            await ctx.respond("The selected user is not a member on this Server!", ephemeral=True)
            return
        elif user == self.bot.user:
            await ctx.respond(f"This is me - the {self.bot.user}", ephemeral=True)
            return
        elif user == ctx.author:
            await ctx.respond("You cannot promote yourself!", ephemeral=True)
            return
        server = ctx.guild
        config = configparser.RawConfigParser()
        configFilePath = r'config.cfg'
        config.read_file(open(configFilePath))
        
        #Role Configuration
        department1_ranks_ids = config.get('Role Management', 'department1_ranks').split(', ')
        department1_ranks = [ctx.guild.get_role(int(role_id)) for role_id in department1_ranks_ids]
        department1_command_id = int(config.get('Role Management', 'department1_command'))
        department1_command_role = server.get_role(department1_command_id)

        #department2_ranks_ids = config.get('Role Management', 'department2_ranks').split(', ')
        #department2_ranks = [ctx.guild.get_role(int(role_id)) for role_id in department2_ranks_ids]
        #department2_command_id = int(config.get('Role Management', 'department2_command'))
        #department2_command_role = server.get_role(department2_command_id)

        #Command implementation
        if department1_command_role in ctx.author.roles:
            ranks = department1_ranks
        #elif department2_command_role in ctx.author.roles:
            #ranks = department2_ranks
        else:
            await ctx.respond("You do not have permission to use this command!", ephemeral=True)
            return
        
        user_roles = user.roles
        user_rank = None
        for rank in ranks:
            if rank in user_roles:
                user_rank = rank
                break
        if user_rank is None:
            await ctx.respond("The selected user does not have a rank that can be promoted!", ephemeral=True)
            return
        current_rank_index = ranks.index(user_rank)
        if current_rank_index == len(ranks) - 1:
            await ctx.respond("The selected user is already at the highest rank!", ephemeral=True)
            return
        new_rank = ranks[current_rank_index + 1]
        await user.remove_roles(user_rank)
        await user.add_roles(new_rank)
        await ctx.respond(f"{user.mention} has been promoted to {new_rank.name}!", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(promotion(bot))