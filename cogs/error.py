"""
File for error handler cog
"""

from logging import Logger

from discord.ext.commands import (
    Cog,
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown,
    Context,
    MissingPermissions,
    MissingRequiredArgument,
)

from models.bot_models import AkatsukiDuCa
from modules.checks_and_utils import get_prefix_for_bot
from modules.exceptions import LangNotAvailable
from modules.lang import get_lang


class ErrorHandler(Cog):
    """
    Cog for handling command errors
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Error Handler loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Error Handler unloaded")
        return await super().cog_unload()

    @Cog.listener("on_command_error")
    async def error_message_handler(
        self, ctx: Context, exception: Exception
    ) -> None:  # pylint: disable=arguments-differ
        """
        Command error handler
        """

        lang = await get_lang(ctx.author.id)
        prefix = await get_prefix_for_bot(ctx.bot, ctx.message)

        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        async def user_no_perms(ctx: Context):
            await ctx.send(lang("main.MissingGuildPermission"))

        async def not_found(ctx: Context):
            await ctx.send(prefix.join(lang("main.CommandNotFound")))

        async def miss_args(ctx: Context):
            await ctx.send(prefix.join(lang("main.MissingRequiredArgument")))

        async def on_cooldown(ctx: Context):
            assert isinstance(exception, CommandOnCooldown)
            await ctx.send(
                str(round(exception.retry_after, 1)).join(
                    lang("main.CommandOnCooldown")
                )
            )

        async def no_lang_available(ctx: Context):
            await ctx.send(lang("main.NotAvailableLanguage"))

        mapping: dict = {
            MissingPermissions: user_no_perms,
            CommandNotFound: not_found,
            MissingRequiredArgument: miss_args,
            CommandOnCooldown: on_cooldown,
            LangNotAvailable: no_lang_available,
        }

        await mapping[exception](ctx)
