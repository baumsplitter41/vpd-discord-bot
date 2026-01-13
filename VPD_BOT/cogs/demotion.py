import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class demotion(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="demotion", description= "Demote a department member to the previous rank")
    async def demotion(
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
        department1_supervisor_role_id = int(config.get('Einweisung', 'department1_supervisor_id'))
        department1_supervisor_role = server.get_role(department1_supervisor_role_id)

        #department2_ranks_ids = config.get('Role Management', 'department2_ranks').split(', ')
        #department2_ranks = [ctx.guild.get_role(int(role_id)) for role_id in department2_ranks_ids]
        #department2_command_id = int(config.get('Role Management', 'department2_command'))
        #department2_command_role = server.get_role(department2_command_id)
        #department2_supervisor_role_id = int(config.get('Einweisung', 'department2_supervisor_id'))
        #department2_supervisor_role = server.get_role(department2_supervisor_role_id)

        #Command implementation
        if department1_command_role in ctx.author.roles:
            ranks = department1_ranks
            supervisor_role = department1_supervisor_role
            command_role = department1_command_role
        #elif department2_command_role in ctx.author.roles:
            #ranks = department2_ranks
            #supervisor_role = department2_supervisor_role
            #command_role = department2_command_role
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
            await ctx.respond("The selected user does not have a rank that can be demoted!", ephemeral=True)
            return
        current_rank_index = ranks.index(user_rank)
        if current_rank_index == 0:
            await ctx.respond("The selected user is already at the lowest rank!", ephemeral=True)
            return
        new_rank = ranks[current_rank_index - 1]
        if new_rank == ranks[5]:
            await user.remove_roles(command_role)
        elif new_rank == ranks[3]:
            await user.remove_roles(supervisor_role)
        await user.remove_roles(user_rank)
        await user.add_roles(new_rank)
        await ctx.respond(f"{user.mention} has been demoted to {new_rank.name}!", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(demotion(bot))