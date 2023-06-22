"""
Toys for kids lmao
"""

from logging import Logger
from random import randint

from discord import Interaction
from discord.app_commands import checks, command
from discord.ext.commands import Cog

from models.bot_models import AkatsukiDuCa
from modules.checks_and_utils import user_cooldown_check


class ToysCog(Cog):
    """
    Lots of toys xD
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Toys Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Toys Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 0.25, key=user_cooldown_check)
    @command(name="random")
    async def random(
        self, interaction: Interaction, min_num: int = 0, max_num: int = 10
    ):
        """
        Feeling lucky?
        """
        await interaction.response.send_message(randint(min_num, max_num))

    @checks.cooldown(1, 0.25, key=user_cooldown_check)
    @command(name="coinflip")
    async def coinflip(self, interaction: Interaction):
        """
        Flip a coin
        """
        await interaction.response.send_message(
            "Heads" if randint(0, 1) == 0 else "Tails"
        )

    @checks.cooldown(1, 0.25, key=user_cooldown_check)
    @command(name="dice")
    async def dice(self, interaction: Interaction):
        """
        Roll a dice
        """
        await interaction.response.send_message(randint(1, 6))
