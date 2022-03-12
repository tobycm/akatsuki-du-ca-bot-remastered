import discord
from discord.ext import commands
from discord import app_commands

class fun(commands.Cog):

    @app_commands.command(name="slap")
    async def slap(self, interaction : discord.Interaction):
        await interaction.response.send_message("slaped!")