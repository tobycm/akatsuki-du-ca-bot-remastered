"""
Models for utils cog
"""

from aioredis import Redis
from discord import Interaction, User
from discord.ui import Select
from models.bot_models import CustomBot

from modules.database_utils import set_user_lang
from modules.vault import get_channel_config


class ChangeLang(Select):
    def __init__(self, bot: CustomBot, author: User):
        self.redis_ins: Redis = bot.redis_ins
        self.bot: CustomBot = bot
        self.author: User = author

        super().__init__(placeholder="Choose language")

    async def callback(self, interaction: Interaction):
        result = self.values[0]
        result = await set_user_lang(self.redis_ins, interaction.user.id, result)

        if result:
            await interaction.response.send_message("\U0001f44c", ephemeral=True)
            return

        error_channel = self.bot.fetch_channel(get_channel_config("error"))
        error_channel.send(
            f"Error changing language, user: {interaction.user.id}, guild: {interaction.guild.id}\n{result}"
        )
        return
