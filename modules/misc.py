"""
Just some checks and utils function
"""

from math import floor

from discord import (
    Color, DMChannel, Embed, GroupChannel, Interaction, Member, Message,
    StageChannel, TextChannel, Thread, User, VoiceChannel
)
from discord.ext.commands import Context

from akatsuki_du_ca import AkatsukiDuCa
from modules.database import get_op, get_prefix
from modules.lang import Lang

global default_prefix
default_prefix: str


def load(prefix: str = "duca!"):
    global default_prefix
    default_prefix = prefix


async def check_owners(
    ctx: Context[AkatsukiDuCa] | Interaction[AkatsukiDuCa]
) -> bool:
    """
    Check if user is owner
    """

    if isinstance(ctx, Interaction):
        ctx = await Context.from_interaction(ctx)

    if await ctx.bot.is_owner(ctx.author):
        return True

    if await get_op(ctx.author.id):
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


def seconds_to_time(seconds: int, double_zero_in_minutes: bool = False) -> str:
    """
    Convert seconds to time in format hh:mm:ss
    """

    hours = floor(seconds / 3600)
    minutes = floor((seconds - hours * 3600) / 60)
    seconds = seconds - hours * 3600 - minutes * 60
    seconds = floor(seconds)

    minutes_str = (
        f"0{minutes}"
        if double_zero_in_minutes and minutes < 10 else f"{minutes}"
    )
    seconds_str = f"0{seconds}" if seconds < 10 else f"{seconds}"

    time = f"{minutes_str}:{seconds_str}"
    if hours != 0:
        time = f"{hours}:{time}"

    return time


async def get_prefix_for_bot(_: AkatsukiDuCa, message: Message) -> str:
    """
    Return the prefix for the bot.
    """

    assert message.guild
    return await get_prefix(message.guild.id) or default_prefix


def rich_embed(embed: Embed, author: User | Member, lang: Lang) -> Embed:
    """
    Added color, author and footer to embed
    """

    footer = lang("main.embed_footer")
    setattr(embed, "color", Color.random())
    embed.set_footer(
        text = footer % str(author), icon_url = author.display_avatar
    )
    return embed


GuildTextableChannel = TextChannel | Thread | VoiceChannel | StageChannel
TextableChannel = GuildTextableChannel | DMChannel | GroupChannel
