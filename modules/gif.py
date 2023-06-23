"""
GIF backend functions.
"""

from random import choice
from typing import Callable

from aiohttp import ClientSession
from discord import Embed, Member, User

Url = str


async def get_gif_url(method: str, api_key: str) -> Url:
    """
    Get a GIF url using search query
    """

    async with ClientSession() as session:
        async with session.get(
            f"https://g.tenor.com/v1/random?q=Anime {method} GIF&key={api_key}&limit=9"
        ) as response:
            return choice((await response.json())["results"])["media"][0]["gif"]["url"]


async def construct_gif_embed(
    author: User | Member,
    target: User | Member,
    method: str,
    api_key: str,
    lang: Callable[[str], str],
) -> Embed:
    """
    Construct a GIF embed
    """

    mid_text = lang(f"gif.{method}.mid_text")

    if method == "slap":
        description = f"{target} {mid_text} {author}"
    else:
        description = f"{author} {mid_text} {target}"
    if method in ["hug", "kick", "poke", "bite", "cuddle"]:
        description += lang(f"gif.{method}.mid_text_2")  # type: ignore

    return Embed(title=lang(f"gif.{method}.title"), description=description).set_image(
        url=await get_gif_url(method, api_key)
    )
