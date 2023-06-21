"""
Just some checks and utils function
"""

from datetime import timedelta
from typing import Union

from aioredis import Redis
from discord import Interaction, Message
from discord.ext.commands import Bot, Context

from models.bot_models import AkatsukiDuCa
from modules.database_utils import get_prefix, get_user_lang
from modules.vault import get_bot_config

DEFAULT_PREFIX = get_bot_config("prefix")


async def check_owners(redis_ins: Redis, ctx: Union[Context, Interaction]) -> bool:
    """
    Check if user is owner
    """

    bot: Bot = ctx.bot if isinstance(ctx, Context) else ctx.client
    author = ctx.author if isinstance(ctx, Context) else ctx.user

    if await bot.is_owner(author):
        return True

    if await redis_ins.hget("op", author.id):
        return True

    return False


def user_cooldown_check(itr: Interaction) -> int:
    """
    User cooldown check
    """

    return itr.user.id


def guild_cooldown_check(itr: Interaction) -> int:
    """
    Guild cooldown check
    """

    if itr.guild is None:  # for typing
        return itr.user.id

    return itr.guild.id


async def return_user_lang(bot, user_id: int) -> dict:
    """
    Return user language as a dict
    """

    bot: AkatsukiDuCa = bot

    lang_option = await get_user_lang(bot.redis_ins, user_id)
    return bot.lang[lang_option] or bot.lang["en-us"]


def seconds_to_time(seconds) -> str:
    """
    Convert seconds to time in format hh:mm:ss
    """

    return str(timedelta(seconds=int(seconds)))


async def get_prefix_for_bot(bot: AkatsukiDuCa, message: Message):
    """
    Return the prefix for the bot.
    """

    if message.guild is None:  # for typing
        return

    return await get_prefix(bot.redis_ins, message.guild.id) or DEFAULT_PREFIX
