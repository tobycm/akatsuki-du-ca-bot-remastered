from random import randint
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot

from modules.checks_and_utils import user_cooldown_check
from modules.log_utils import command_log

class ToysCog(Cog):
    def __init__(self, bot : Bot) -> None:
        self.bot = bot
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "random")
    async def random(self, interaction : Interaction, min : int = 0, max : int = 10):
        """
        Feeling lucky?
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        await interaction.response.send_message(randint(min, max))
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "coinflip")
    async def coinflip(self, interaction : Interaction):
        """
        Flip a coin
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        
        if randint(0, 1) == 0:
            coin = "Heads"
        else:
            coin = "Tails"
        await interaction.response.send_message(coin)
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "dice")
    async def dice(self, interaction : Interaction):
        """
        Roll a dice
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        
        await interaction.response.send_message(randint(1, 6))