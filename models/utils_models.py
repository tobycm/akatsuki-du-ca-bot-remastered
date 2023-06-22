"""
Models for utils cog
"""

from typing import Union

from discord import Interaction, Member, User
from discord.ext.commands import Bot
from discord.ui import Select

from modules.database_utils import set_user_lang


class ChangeLang(Select):
    """
    Change language Select menu class
    """

    def __init__(self, author: Union[User, Member]):
        self.author = author

        super().__init__(placeholder="Choose language")

    async def callback(self, interaction: Interaction):
        await set_user_lang(interaction.user.id, self.values[0])

        await interaction.response.send_message("\U0001f44c", ephemeral=True)
        return
