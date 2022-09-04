"""
Models for utils cog
"""

from aioredis import Redis

from discord import Interaction, User
from discord.ui import Select
from discord.ext.commands import Bot

from modules.database_utils import set_user_lang


class ChangeLang(Select):
    """
    Change language Select menu class
    """

    def __init__(self, bot: Bot, author: User):
        self.redis_ins: Redis = bot.redis_ins
        self.bot: Bot = bot
        self.author: User = author

        super().__init__(placeholder="Choose language")

    async def callback(self, interaction: Interaction):
        result = self.values[0]
        result = await set_user_lang(self.redis_ins, interaction.user.id, result)

        await interaction.response.send_message("\U0001f44c", ephemeral=True)
        return
