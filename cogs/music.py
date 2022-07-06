from discord import Interaction, app_commands
from discord.ext.commands import Cog

from modules.checks_and_utils import user_cooldown_check

class RadioMusic(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 10, key = user_cooldown_check)
    @app_commands.command(name = "suggest")
    async def suggest(self, interaction : Interaction, song : str):
        suggests_channel = await self.bot.get_channel(957341782721585223)