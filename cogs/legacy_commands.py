"""
These commands are for Toby for trolling only xd
"""

from logging import Logger
from typing import Optional

from discord import utils
from discord.ext.commands import (
    Bot,
    Cog,
    Context,
    MissingRequiredArgument,
    NotOwner,
    command,
)

from models.bot_models import AkatsukiDuCa
from modules.checks_and_utils import check_owners


class LegacyCommands(Cog):
    """
    Commands Toby use with bots
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Legacy Command loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Legacy Command unloaded")
        return await super().cog_unload()

    @command(name="say")
    async def say(self, ctx: Context, *, value: str):
        """
        Basically echo
        """

        if not await check_owners(ctx):
            raise NotOwner
        if value == "":
            raise MissingRequiredArgument  # type: ignore

        await ctx.message.delete()
        return await ctx.send(value)

    @command(name="sayemoji")
    async def sayemoji(
        self,
        ctx: Context,
        emoji_name: Optional[str] = None,
        guild_id: Optional[int] = None,
    ):
        """
        Find the emoji and send it
        """

        if emoji_name is None:
            raise MissingRequiredArgument  # type: ignore

        assert ctx.guild

        if guild_id is None:
            guild_emojis = ctx.guild.emojis
        else:
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                await ctx.send("Guild not found")
            guild_emojis = self.bot.get_guild(guild_id).emojis  # type: ignore

        emoji = utils.get(guild_emojis, name=emoji_name)
        await ctx.message.delete()
        await ctx.send(str(emoji) or "lmao")
