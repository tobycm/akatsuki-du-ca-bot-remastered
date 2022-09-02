"""
Just some checks and utils function
"""

from datetime import timedelta
from aioredis import Redis
from discord import Interaction
from discord.ext.commands import Context
from models.bot_models import CustomBot

from modules.database_utils import get_user_lang


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


async def return_user_lang(bot: CustomBot, user_id: int) -> dict:
    """
    Return user language as a dict
    """

    lang_option = await get_user_lang(bot.redis_ins, user_id)
    return bot.lang[lang_option]


def seconds_to_time(seconds) -> str:
    """
    Convert seconds to time in format hh:mm:ss
    """

    return str(timedelta(seconds=int(seconds)))
