"""
Just some checks and utils function
"""

from datetime import timedelta
from random import random
from typing import Callable

from discord import Color, Embed, Interaction, Member, Message, User
from discord.ext.commands import Context

from models.bot_models import AkatsukiDuCa
from modules.database import get_op, get_prefix

global DEFAULT_PREFIX


def load(prefix: str = "duca!"):
    global DEFAULT_PREFIX
    DEFAULT_PREFIX = prefix


async def check_owners(ctx: Context[AkatsukiDuCa] | Interaction[AkatsukiDuCa]) -> bool:
    """
    Check if user is owner
    """

    bot = ctx.bot if isinstance(ctx, Context) else ctx.client
    author = ctx.author if isinstance(ctx, Context) else ctx.user

    if await bot.is_owner(author):
        return True

    if await get_op(author.id):
        return True

    return False


def user_cooldown_check(interaction: Interaction) -> int:
    """
    User cooldown check
    """

    return interaction.user.id


def guild_cooldown_check(interaction: Interaction) -> int:
    """
    Guild cooldown check
    """

    assert interaction.guild
    return interaction.guild.id


def seconds_to_time(seconds) -> str:
    """
    Convert seconds to time in format hh:mm:ss
    """

    return str(timedelta(seconds=int(seconds)))


async def get_prefix_for_bot(bot: AkatsukiDuCa, message: Message) -> str:
    """
    Return the prefix for the bot.
    """

    assert message.guild
    return await get_prefix(message.guild.id) or DEFAULT_PREFIX


def random_color() -> Color:
    """
    Make a random Color
    """

    return Color(int(0xFFFFFF * (1.0 - (0.5 * random()))))


def rich_embed(
    embed: Embed, author: User | Member, lang: Callable[[str], str]
) -> Embed:
    """
    Added color, author and footer to embed
    """

    footer = lang("main.EmbedFooter")
    embed.color = random_color()
    text = f"{footer} {author.name}#{author.discriminator}"
    embed.set_footer(text=text, icon_url=author.display_avatar)
    return embed
