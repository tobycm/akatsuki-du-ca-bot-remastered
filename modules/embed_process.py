"""
Embed related functions
"""

from random import random
from discord import Color, Embed
from discord.abc import User


def random_color() -> Color:
    """
    Make a random Color
    """

    return Color(int(0xffffff * (1.0 - (0.5 * random()))))


def rich_embeds(embed: Embed, author: User, lang: dict = None) -> Embed:
    """
    Added color, author and footer to embed
    """

    if lang is None:
        lang = {"EmbedFooter": "Requested by: "}

    footer = lang["EmbedFooter"]
    embed.color = random_color()
    text = f"{footer} {author.name}#{author.discriminator}"
    embed.set_footer(text=text, icon_url=author.display_avatar)
    return embed
