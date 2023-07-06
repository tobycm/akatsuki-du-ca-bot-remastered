"""
Embed related functions
"""

from random import random
from typing import Callable, Union

from discord import Color, Embed, Member
from discord.abc import User


def random_color() -> Color:
    """
    Make a random Color
    """

    return Color(int(0xFFFFFF * (1.0 - (0.5 * random()))))


def rich_embeds(embed: Embed, author: Union[User, Member], lang: Callable[[str], str]) -> Embed:
    """
    Added color, author and footer to embed
    """

    footer = lang("main.EmbedFooter")
    embed.color = random_color()
    text = f"{footer} {author.name}#{author.discriminator}"
    embed.set_footer(text=text, icon_url=author.display_avatar)
    return embed
