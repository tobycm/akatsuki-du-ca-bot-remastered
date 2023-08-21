"""
GIF backend functions.
"""

from random import choice
from typing import Callable

from aiohttp import ClientSession
from discord import Embed, Member

Url = str

global session
session: ClientSession


def load(sess: ClientSession):
    global session
    session = sess


async def get_gif_url(method: str, api_key: str) -> Url:
    """
    Get a GIF url using search query
    """

    async with session.get(
        f"https://g.tenor.com/v1/random?q=Anime {method} GIF&key={api_key}&limit=9"
    ) as response:
        return choice((await response.json())["results"])["media"][0]["gif"]["url"]


async def construct_gif_embed(
    author: Member,
    target: Member,
    method: str,
    api_key: str,
    lang: Callable[[str], str],
) -> Embed:
    """
    Construct a GIF embed
    """

    description = lang(f"gif.{method}.text") % (author.mention, target.mention)

    return Embed(title=lang(f"gif.{method}.title"), description=description).set_image(
        url=await get_gif_url(method, api_key)
    )