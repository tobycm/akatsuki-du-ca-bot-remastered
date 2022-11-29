"""
Just some checks and utils function
"""

from datetime import timedelta
from aioredis import Redis

from discord import Interaction, Message
from discord.ext.commands import Context, Bot

from modules.database_utils import get_prefix, get_user_lang
from modules.vault import get_bot_config

DEFAULT_PREFIX = get_bot_config("prefix")

async def check_owners(redis_ins: Redis, ctx: Context or Interaction) -> bool:
    """
    Check if user is owner
    """

    result = await redis_ins.hget("op", ctx.author.id)
    if result is None:
        return False
    return True


def user_cooldown_check(itr: Interaction) -> bool:
    """
    User cooldown check
    """

    return itr.user.id


def guild_cooldown_check(itr: Interaction) -> bool:
    """
    Guild cooldown check
    """

    return itr.guild.id


async def return_user_lang(bot: Bot, user_id: int) -> dict:
    """
    Return user language as a dict
    """

    lang_option = await get_user_lang(bot.redis_ins, user_id)
    return bot.lang[lang_option] if lang_option is not None else bot.lang["en-us"]


def seconds_to_time(seconds) -> str:
    """
    Convert seconds to time in format hh:mm:ss
    """

    return str(timedelta(seconds=int(seconds)))

async def get_prefix_for_bot(bot, message: Message):  # pylint: disable=redefined-outer-name
    """
    Return the prefix for the bot.
    """

    prefix = await get_prefix(bot.redis_ins, message.guild.id)
    if prefix is None:
        return DEFAULT_PREFIX
    return prefix
