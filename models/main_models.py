"""
Models for main file
"""

from discord import Interaction
from discord.ui import Select

from modules.database import set_user_lang
from modules.lang import get_lang


class LangSel(Select):
    """
    Make a language selection Select
    """

    def __init__(self, lang: list[dict]) -> None:
        self.lang = lang

        super().__init__(placeholder="Choose your language: ")

    async def callback(self, interaction: Interaction):
        await set_user_lang(user_id=interaction.user.id, lang_option=self.values[0])

        await interaction.response.send_message(
            content=(await get_lang(interaction.user.id))("main.LangSwitched"),
            ephemeral=True,
        )
        return
