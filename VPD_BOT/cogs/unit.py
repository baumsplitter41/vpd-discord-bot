import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class unit(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="unit", description= "Add or remove a department member to/from a unit")
    async def unit(
        self,
        ctx,
        user: str = Option(discord.User, "Select User", required=True),
        unit: str = Option(str, "Select Unit", required=True)
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

#Role configuration
        department1_role_id = config.get('Einweisung', 'department1_role_id')
        department1_role = ctx.guild.get_role(int(department1_role_id))
        #department2_role_id = config.get('Role Management', 'department2_role_id')
        #department2_role = ctx.guild.get_role(int(department2_role_id))
        department1_head_unit_id = int(config.get('Role Management', 'department1_head_unit'))
        department1_head_unit = server.get_role(department1_head_unit_id)
        department1_supervisor_role_id = int(config.get('Einweisung', 'department1_supervisor_id'))
        department1_supervisor_role = server.get_role(department1_supervisor_role_id)

        department1_units_id = config.get('Role Management', 'department1_units').split(', ')
        department1_units = [ctx.guild.get_role(int(role_id)) for role_id in department1_units_id]
        #department2_units_id = config.get('Role Management', 'department2_units').split(', ')
        #department2_units = [ctx.guild.get_role(int(role_id)) for role_id in
        #department2_head_unit_id = int(config.get('Role Management', 'department2_head_unit'))
        #department2_head_unit = server.get_role(department2_head_unit_id)
        #department2_supervisor_role_id = int(config.get('Einweisung', 'department2_supervisor_id'))
        #department2_supervisor_role = server.get_role(department2_supervisor_role_id)

        if department1_role in user.roles:
            units = department1_units
            supervisor_role = department1_supervisor_role
            head_unit_role = department1_head_unit
        #elif department2_role in user.roles:
            #units = "department2"
            #supervisor_role = department2_supervisor_role
            #head_unit_role = department2_head_unit
        else:
            await ctx.respond("The selected user is not a member of any department!", ephemeral=True)
            return
        

#Command implementation
        if unit == "Detective":
            unit_role = units[0]
        elif unit == "SWAT":
            unit_role = units[1]
        elif unit == "Canine":
            unit_role = units[2]
        elif unit == "Air Support":
            unit_role = units[3]
        elif unit == "Help":
            unit_role = None
            help_text = "Available Units:\n- Detective\n- SWAT\n- Canine\n- Air Support"
            await ctx.respond(help_text, ephemeral=True)
            return
        else:
            await ctx.respond("The selected unit does not exist! Use Help for a list of available units.", ephemeral=True)
            return
        if supervisor_role in ctx.author.roles or head_unit_role in ctx.author.roles:
            if unit_role in user.roles:
                await user.remove_roles(unit_role)
                await ctx.respond(f"The user {user.mention} has been removed from the unit successfully!", ephemeral=True)
            else:
                await user.add_roles(unit_role)
                await ctx.respond(f"The user {user.mention} has been added to the unit successfully!", ephemeral=True)
        else:
            await ctx.respond("You do not have permission to use this command!", ephemeral=True)
            return
        
def setup(bot: discord.Bot):
    bot.add_cog(unit(bot))