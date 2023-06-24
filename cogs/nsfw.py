"""
Not Safe for Work commands. 0_0
"""

from discord import Embed, Interaction, TextChannel, Thread
from discord.app_commands import checks, command
from discord.ext.commands import GroupCog

from akatsuki_du_ca import AkatsukiDuCa
from modules.lang import get_lang
from modules.misc import rich_embed, user_cooldown_check
from modules.waifu import random_image


class NSFWCog(GroupCog, name="nsfw"):
    """
    NSFW related commands.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
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

        assert isinstance(interaction.channel, TextChannel | Thread)

        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                lang("nsfw.PlsGoToNSFW"), ephemeral=True
            )

        image = await random_image(nsfw=True)

        await interaction.response.send_message(
            embed=rich_embed(
                Embed(
                    title="0.0",
                    description=lang("fun.PoweredByWaifuim")
                    + "\n"
                    + f"[Source]({image})",
                ),
                interaction.user,
                lang,
            ).set_image(url=str(image))
        )
