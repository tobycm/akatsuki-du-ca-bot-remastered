from discord import Color, Embed
from discord.abc import User
from random import random

def random_color() -> Color:
    return Color(int(0xffffff * (1.0 - (0.5 * random()))))

def rich_embeds(embed : Embed, author : User, lang : dict = {"EmbedFooter": "Requested by: "}) -> Embed:
    footer = lang["EmbedFooter"]
    embed.color = random_color()
    text = f"{footer} {author.name}#{author.discriminator}"
    embed.set_footer(text = lang["EmbedFooter"], icon_url = author.display_avatar)
    return embed