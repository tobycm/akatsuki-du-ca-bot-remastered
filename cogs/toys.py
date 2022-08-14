from random import randint
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot

from modules.checks_and_utils import user_cooldown_check


class ToysCog(Cog):
    def __init__(self, bot : Bot) -> None:
        self.bot = bot
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "random")
    async def random(self, itr : Interaction, min : int = 0, max : int = 10):
        """
        Feeling lucky?
        """
        await itr.response.send_message(randint(min, max))
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "coinflip")
    async def coinflip(self, itr : Interaction):
        """
        Flip a coin
        """
        
        if randint(0, 1) == 0:
            coin = "Heads"
        else:
            coin = "Tails"
        await itr.response.send_message(coin)
        
    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "dice")
    async def dice(self, itr : Interaction):
        """
        Roll a dice
        """
        await itr.response.send_message(randint(1, 6))