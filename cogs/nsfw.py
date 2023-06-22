"""
Not Safe for Work commands. 0_0
"""

from logging import Logger

from discord import Embed, Interaction
from discord.app_commands import checks, command
from discord.ext.commands import Bot, GroupCog

from modules.checks_and_utils import user_cooldown_check
from modules.embed_process import rich_embeds
from modules.lang import get_lang, get_lang_by_address
from modules.nsfw import get_nsfw


class NSFWCog(GroupCog, name="nsfw"):
    """
    NSFW related commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("NSFW Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("NSFW Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="art")
    async def nsfw(self, interaction: Interaction):
        """
        Good nsfw art huh?
        """

        lang = await get_lang(interaction.user.id)

        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                get_lang_by_address("nsfw.PlsGoToNSFW", lang), ephemeral=True
            )

        url, source = await get_nsfw()

        await interaction.response.send_message(
            embed=rich_embeds(
                Embed(
                    title="0.0",
                    description=get_lang_by_address("fun.PoweredByWaifuim", lang)
                    + "\n"
                    + f"Source: [{source}]({source})",
                ),
                interaction.user,
                lang,
            ).set_image(url=url)
        )
