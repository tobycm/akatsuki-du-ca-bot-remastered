"""
File for error handler cog
"""

from logging import Logger
from discord.ext.commands import (
    Context,
    MissingPermissions,
    CommandInvokeError,
    CommandNotFound,
    MissingRequiredArgument,
    CommandOnCooldown,
    Cog,
    Bot
)

from modules.checks_and_utils import get_prefix_for_bot, return_user_lang
from modules.exceptions import LangNotAvailable

class ErrorHandler(Cog):
    """
    Cog for handling command errors
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Error Handler loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Error Handler unloaded")
        return await super().cog_unload()

    @Cog.listener("on_command_error")
    async def error_message_handler(self, ctx: Context, exception: Exception) -> None: # pylint: disable=arguments-differ
        """
        Command error handler
        """

        lang = await return_user_lang(self, ctx.author.id)
        prefix = await get_prefix_for_bot(self, ctx.message)

        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        async def user_no_perms(ctx: Context):
            await ctx.send(lang["MissingGuildPermission"])

        async def not_found(ctx: Context):
            await ctx.send(prefix.join(lang["CommandNotFound"]))

        async def miss_args(ctx: Context):
            await ctx.send(prefix.join(lang["MissingRequiredArgument"]))

        async def on_cooldown(ctx: Context):
            exception: CommandOnCooldown = exception
            await ctx.send(str(round(exception.retry_after, 1)).join(lang["CommandOnCooldown"]))

        async def no_lang_available(ctx: Context):
            await ctx.send(lang["NotAvailableLanguage"])

        mapping = {
            MissingPermissions: user_no_perms,
            CommandNotFound: not_found,
            MissingRequiredArgument: miss_args,
            CommandOnCooldown: on_cooldown,
            LangNotAvailable: no_lang_available,
        }

        await mapping[exception](ctx)
