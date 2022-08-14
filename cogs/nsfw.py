"""
Not Safe for Work commands. 0_0
"""

from discord import Embed, Interaction, app_commands
from discord.ext.commands import GroupCog, Bot

from modules.embed_process import rich_embeds
from modules.nsfw import get_nsfw
from modules.checks_and_utils import user_cooldown_check, return_user_lang


class NSFWCog(GroupCog, name="nsfw"):
    """
    NSFW related commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    @app_commands.checks.cooldown(1, 1, key=user_cooldown_check)
    @app_commands.command(name="art")
    async def nsfw(self, itr: Interaction):
        """
        Good nsfw art huh?
        """

        author = itr.user
        lang = await return_user_lang(self, author.id)
        if not itr.channel.is_nsfw():
            await itr.response.send_message(lang["nsfw"]["PlsGoToNSFW"], ephemeral=True)

        url, source = await get_nsfw()

        await itr.response.send_message(
            embed=rich_embeds(
                Embed(title="0.0",
                      description=f"{lang['fun']['PoweredByWaifuim']}\nSource: [{source}]({source})"),
                author,
                lang["main"]
            ).set_image(url=url)
        )
