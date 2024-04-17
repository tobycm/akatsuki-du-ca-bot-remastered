"""
Toys for kids lmao
"""

from random import randint

from discord import Interaction
from discord.app_commands import checks, command
from discord.ext.commands import Cog

from akatsuki_du_ca import AkatsukiDuCa
from modules.log import logger
from modules.misc import user_cooldown_check


class ToysCog(Cog):
    """
    Lots of toys xD
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        logger.info("Toys Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Toys Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 0.25, key = user_cooldown_check)
    @command(name = "random")
    async def random(
        self, interaction: Interaction, min: int = 0, max: int = 10
    ):
        """
        Feeling lucky?
        """
        await interaction.response.send_message(randint(min, max))

    @checks.cooldown(1, 0.25, key = user_cooldown_check)
    @command(name = "coinflip")
    async def coinflip(self, interaction: Interaction):
        """
        Flip a coin
        """
        await interaction.response.send_message(
            "Heads" if randint(0, 1) == 0 else "Tails"
        )

    @checks.cooldown(1, 0.25, key = user_cooldown_check)
    @command(name = "dice")
    async def dice(self, interaction: Interaction):
        """
        Roll a dice
        """
        await interaction.response.send_message(randint(1, 6))
