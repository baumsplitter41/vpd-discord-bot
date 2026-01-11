import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class einweisung(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


#Command initialization
    @slash_command(name="einweisung", description="Freischalten eines User nach der Einweisung")
    async def einweisung(
            self,
            ctx,
            user: discord.User = Option(discord.User, "Select User"),
        ):
        if user is None:
            user = ctx.author
        elif user not in ctx.guild.members:
            await ctx.respond("The selected user is not a member on this Server!", ephemeral=True)
            return
        elif user == self.bot.user:
            await ctx.respond(f"This is me - the {self.bot.user}", ephemeral=True)
            return
        server = ctx.guild

        config = configparser.RawConfigParser()
        configFilePath = r'config.cfg'
        config.read_file(open(configFilePath))

#Role Configuration
        acces_role_id = int(config.get('Einweisung', 'acces_role_id'))
        acces_role = server.get_role(acces_role_id)


        department1_supervisor_id = int(config.get('Einweisung', 'department1_supervisor_id'))
        department1_role_id = int(config.get('Einweisung', 'department1_role_id'))
        department1_role = server.get_role(department1_role_id)
        department1_supervisor = server.get_role(department1_supervisor_id)
        department1_deputy_id = int(config.get('Einweisung', 'department1_deputy_id'))
        department1_deputy = server.get_role(department1_deputy_id)

        #department2_supervisor_id = int(config.get('Einweisung', 'department2_supervisor_id'))
        #department2_role_id = int(config.get('Einweisung', 'department2_role_id'))
        #department2_role = server.get_role(department2_role_id)
        #department2_supervisor = server.get_role(department2_supervisor_id)
        #department2_deputy_id = int(config.get('Einweisung', 'department2_deputy_id'))
        #department2_deputy = server.get_role(department2_deputy_id)

#Command implemetation
        if department1_role is None or department1_supervisor is None or acces_role is None or department1_deputy is None:
            await ctx.respond("One or more roles are not configured properly!", ephemeral=True)
            return
        
        if department1_supervisor in ctx.author.roles:
            n = 1
        #elif department2_supervisor in ctx.author.roles:
            #n = 2
        else: 
            await ctx.respond("You don't have permission to use this command!", ephemeral=True)
            return

        try:
            if n == 1:
                await user.add_roles(department1_role, department1_deputy, acces_role)
            #elif n == 2:
               # await user.add_roles(department2_role, department2_deputy, acces_role)
        except discord.Forbidden:
            await ctx.respond("I don't have permission to assign roles!", ephemeral=True)
            return
        
        embed = discord.Embed(title="Einweisung abgeschlossen", color=0x00ff00)
        embed.add_field(name="User Freigeschaltet:", value=f"{user.mention} wurde erfolgreich freigeschaltet.", inline=False)




        await ctx.respond(embed=embed, ephemeral=True)



def setup(bot: discord.Bot):
    bot.add_cog(einweisung(bot))
