"""
File for error handler cog
"""

from discord.ext.commands import (
    Cog, CommandInvokeError, CommandNotFound, CommandOnCooldown, Context,
    MissingPermissions, MissingRequiredArgument
)

from akatsuki_du_ca import AkatsukiDuCa
from modules.exceptions import LangNotAvailable
from modules.lang import get_lang
from modules.log import logger
from modules.misc import get_prefix_for_bot


class ErrorHandler(Cog):
    """
    Cog for handling command errors
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        logger.info("Error Handler loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Error Handler unloaded")
        return await super().cog_unload()

    @Cog.listener("on_command_error")
    async def error_message_handler(
        self, ctx: Context, exception: Exception
    ) -> None:
        """
        Command error handler
        """

        lang = await get_lang(ctx.author.id)
        prefix = await get_prefix_for_bot(ctx.bot, ctx.message)

        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        async def user_no_perms():
            await ctx.send(lang("main.missing_guild_permission") % prefix)

        async def not_found():
            await ctx.send(lang("main.command_not_found") % prefix)

        async def miss_args():
            await ctx.send(lang("main.missing_required_argument") % prefix)

        async def on_cooldown():
            assert isinstance(exception, CommandOnCooldown)
            await ctx.send(
                lang("main.command_on_cooldown") %
                round(exception.retry_after, 1)
            )

        async def no_lang_available():
            await ctx.send(lang("main.language_not_available"))

        mapping: dict = {
            MissingPermissions: user_no_perms,
            CommandNotFound: not_found,
            MissingRequiredArgument: miss_args,
            CommandOnCooldown: on_cooldown,
            LangNotAvailable: no_lang_available,
        }

        await mapping[exception]()
