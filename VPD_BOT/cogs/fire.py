import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class fire(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="fire", description= "Fire a department member from their position")
    async def fire(
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
        department1_role_id = config.get('Einweisung', 'department1_role_id')
        department1_role = server.get_role(int(department1_role_id))
        department1_ranks_ids = config.get('Role Management', 'department1_ranks').split(', ')
        department1_ranks = [ctx.guild.get_role(int(role_id)) for role_id in department1_ranks_ids]
        department1_command_id = int(config.get('Role Management', 'department1_command'))
        department1_command_role = server.get_role(department1_command_id)
        department1_supervisor_role_id = int(config.get('Einweisung', 'department1_supervisor_id'))
        department1_supervisor_role = server.get_role(department1_supervisor_role_id)
        department1_units_id = config.get('Role Management', 'department1_units').split(', ')
        department1_units = [ctx.guild.get_role(int(role_id)) for role_id in department1_units_id]
        #department2_role_id = config.get('Role Management', 'department2_role_id')
        #department2_role = server.get_role(int(department2_role_id))
        #department2_ranks_ids = config.get('Role Management', 'department2_ranks').split(', ')
        #department2_ranks = [ctx.guild.get_role(int(role_id)) for role_id in department2_ranks_ids]
        #department2_command_id = int(config.get('Role Management', 'department2_command'))
        #department2_command_role = server.get_role(department2_command_id)
        #department2_supervisor_role_id = int(config.get('Einweisung', 'department2_supervisor_id'))
        #department2_supervisor_role = server.get_role(department2_supervisor_role_id)
        #department2_units_id = config.get('Role Management', 'department2_units').split(', ')
        #department2_units = [ctx.guild.get_role(int(role_id)) for role_id in department2_units_id]


#Command implementation
        remove_access_role_on_fire = config.get('Role Management', 'remove_access_role_on_fire')
        remove_access_role_on_fire = str(remove_access_role_on_fire).lower()

        if department1_command_role in ctx.author.roles:
            ranks = department1_ranks
            supervisor_role = department1_supervisor_role
            command_role = department1_command_role
            units = department1_units
            department = department1_role
        #elif department2_command_role in ctx.author.roles:
            #ranks = department2_ranks
            #supervisor_role = department2_supervisor_role
            #command_role = department2_command_role
            #units = department2_units
            #department = department2_role
        else:
            await ctx.respond("The User is not Part of your Department", ephemeral=True)
            return
        
        if command_role in ctx.author.roles:
            user_roles = user.roles
            if remove_access_role_on_fire == "true":
                access_role_id = config.get('Einweisung', 'acces_role_id')
                access_role = server.get_role(int(access_role_id))
                await user.remove_roles(access_role)
            await user.remove_roles(department)
            for rank in ranks:
                if rank in user_roles:
                    await user.remove_roles(rank)
            for unit in units:
                if unit in user_roles:
                    await user.remove_roles(unit)
            if supervisor_role in user_roles:
                await user.remove_roles(supervisor_role)
            elif command_role in user_roles:
                await user.remove_roles(command_role)
            await ctx.respond(f"{user.mention} has been fired from their position and all department roles have been removed.", ephemeral=True)
        else:
            await ctx.respond("You do not have permission to use this command!", ephemeral=True)
            return
        
def setup(bot: discord.Bot):
    bot.add_cog(fire(bot))