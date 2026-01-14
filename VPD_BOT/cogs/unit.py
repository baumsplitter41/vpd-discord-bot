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
        #unit: str = Option(str, "Select Unit", required=True),
        unit=["Detective", "SWAT", "Canine", "Air Support"]
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
        department1_role_id = config.get('Einweisung', 'department1_role_id').split(', ')
        department1_role = ctx.guild.get_role(int(department1_role_id))
        #department2_role_id = config.get('Role Management', 'department2_role_id').split(', ')
        #department2_role = ctx.guild.get_role(int(department2_role_id))

        department1_units_id = config.get('Role Management', 'department1_units').split(', ')
        department1_units = [ctx.guild.get_role(int(role_id)) for role_id in department1_units_id]
        #department2_units_id = config.get('Role Management', 'department2_units').split(', ')
        #department2_units = [ctx.guild.get_role(int(role_id)) for role_id in

        if department1_role in user.roles:
            units = "department1"
        #elif department2_role in user.roles:
            #units = "department2"
        else:
            await ctx.respond("The selected user is not a member of any department!", ephemeral=True)
            return
        

#Command implementation
        if unit == "Detective":
            unit_role = int(department1_units[0])
        elif unit == "SWAT":
            unit_role = int(department1_units[1])
        elif unit == "Canine":
            unit_role = int(department1_units[2])
        elif unit == "Air Support":
            unit_role = int(department1_units[3])
        else:
            await ctx.respond("The selected unit does not exist!", ephemeral=True)
            return






def setup(bot: discord.Bot):
    bot.add_cog(unit(bot))