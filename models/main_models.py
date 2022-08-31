"""
Models for main file
"""

from typing import List
from aioredis import Redis
from discord import Interaction
from discord.ui import Select

from modules.database_utils import set_user_lang


class LangSel(Select):
    """
    Make a music selection Select
    """

    def __init__(self, redis_ins: Redis, lang: List[dict]) -> None:
        self.redis_ins: Redis = redis_ins
        self.lang: List[dict] = lang

        super().__init__(placeholder="Choose your language: ")

    async def callback(self, interaction: Interaction):
        await set_user_lang(
            redis_ins=self.redis_ins,
            user_id=interaction.user.id,
            lang=self.values[0]
        )

        await interaction.response.send_message(
            content=self.lang[self.values[0]]["main"]["LangSwitched"],
            ephemeral=True
        )
        return
