"""
Embed related functions
"""

from random import random

from discord import Color, Embed
from discord.abc import User

from modules.lang import get_lang_by_address


def random_color() -> Color:
    """
    Make a random Color
    """

    return Color(int(0xFFFFFF * (1.0 - (0.5 * random()))))


def rich_embeds(embed: Embed, author: User, lang: dict) -> Embed:
    """
    Added color, author and footer to embed
    """

    footer = get_lang_by_address("main.EmbedFooter", lang)
    embed.color = random_color()
    text = f"{footer} {author.name}#{author.discriminator}"
    embed.set_footer(text=text, icon_url=author.display_avatar)
    return embed
