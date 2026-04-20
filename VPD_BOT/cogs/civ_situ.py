import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command
import configparser


class civsitu(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    def _load_config(self):
        config = configparser.ConfigParser()
        configFilePath = r'config.cfg'
        config.read(configFilePath)
        return config
    def _get_situ_channel(self):
        config = self._load_config()
        situ_channel_id = int(config["Civ"]["situ_channel_id"])
        situ_channel = self.bot.get_channel(situ_channel_id)
        if situ_channel is None:
            print(f"Log channel with ID {situ_channel_id} not found.")
            return None
        return situ_channel
    """def _get_situ_team_channel(self):
        config = self._load_config()
        situ_team_channel_id = int(config["Civ"]["situ_team_channel_id"])
        situ_team_channel = self.bot.get_channel(situ_team_channel_id)
        if situ_team_channel is None:
            print(f"Log channel with ID {situ_team_channel_id} not found.")
            return None
        return situ_team_channel"""

    #Modal form
    class Situ(discord.ui.Modal):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_item(discord.ui.InputText(label="Teilnehmende Spieler", placeholder="Gib die Namen der teilnehmenden Spieler abgesehen von dir ein.", required=False, ))
            self.add_item(discord.ui.InputText(label="Benötigte Ausrüstung", placeholder="Gib die benötigte Ausrüstung an (Drogen, Waffen, etc.)."))
            self.add_item(discord.ui.InputText(label="Situationsbeschreibung", style=discord.InputTextStyle.long, placeholder="Beschreibe die Situation so detailliert wie möglich (Was? Wo? Wie?)."))
            self.add_item(discord.ui.InputText(label="Besonderheiten", placeholder="Langzeitsituationen, besondere Umstände, etc.", required=False))

        #Output of the Modal form
        async def callback(self, interaction: discord.Interaction):
            #Public embed with less information
            embed_pub = discord.Embed(title="Aktive Situation")
            embed_pub.add_field(name="Ersteller", value=interaction.user.mention, inline=False)
            embed_pub.add_field(name="Teilnehmer", value=self.children[0].value, inline=False)
            embed_pub.add_field(name="Long Input", value=self.children[1].value, inline=False)
            self.embed_pub = embed_pub
            await interaction.response.send_message("Die Situation wurde erfolgreich erstellt und veröffentlicht.", ephemeral=True)
            situ_channel = civsitu._get_situ_channel(self)
            msg = await situ_channel.send(embeds=[embed_pub])
            name = f"situation-{interaction.user.name}"
            thread =await msg.create_thread(name=name, auto_archive_duration=1440)

            #embed with more information sent into a thread attached to the public embed
            embed_team = discord.Embed(title="Aktive Situation")
            embed_team.add_field(name="Ersteller", value=interaction.user.mention, inline=False)
            embed_team.add_field(name="Teilnehmer", value=self.children[0].value, inline=False)
            embed_team.add_field(name="Benötigte Ausrüstung", value=self.children[1].value, inline=False)
            embed_team.add_field(name="Situationsbeschreibung", value=self.children[2].value, inline=False)
            embed_team.add_field(name="Besonderheiten", value=self.children[3].value, inline=False)
            self.embed_team = embed_team
            await thread.send(embeds=[embed_team])
            await thread.send("Please wait with the start of your situation unil a (civ-) team member approved your situation.")


    #Slash command to trigger the Modal form
    @slash_command()
    async def civsitu(self, ctx: discord.ApplicationContext):
        """Start a new civ-RP situation."""
        modal = self.Situ(title="Create a new civ-rp situation") # type: ignore
        await ctx.send_modal(modal)
 

def setup(bot: discord.Bot):
    bot.add_cog(civsitu(bot))
