"""
Toys for kids lmao
"""

from random import randint
from discord import Interaction, app_commands
from discord.ext.commands import Cog
from models.bot_models import CustomBot

from modules.checks_and_utils import user_cooldown_check


class ToysCog(Cog):
    """
    Lots of toys xD
    """

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @app_commands.checks.cooldown(1, 0.25, key=user_cooldown_check)
    @app_commands.command(name="random")
    async def random(self, itr: Interaction, min_num: int = 0, max_num: int = 10):
        """
        Feeling lucky?
        """
        await itr.response.send_message(randint(min_num, max_num))

    @app_commands.checks.cooldown(1, 0.25, key=user_cooldown_check)
    @app_commands.command(name="coinflip")
    async def coinflip(self, itr: Interaction):
        """
        Flip a coin
        """

        if randint(0, 1) == 0:
            coin = "Heads"
        else:
            coin = "Tails"
        await itr.response.send_message(coin)

    @app_commands.checks.cooldown(1, 0.25, key=user_cooldown_check)
    @app_commands.command(name="dice")
    async def dice(self, itr: Interaction):
        """
        Roll a dice
        """
        await itr.response.send_message(randint(1, 6))
