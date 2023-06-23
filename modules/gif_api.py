"""
GIF backend functions.
"""

from random import choice
from typing import Callable, Union

from aiohttp import ClientSession
from discord import Embed, Member, User

from modules.vault import get_api_key

Url = str


async def get_gif_url(method: str) -> Url:
    """
    Get a GIF url using search query
    """

    async with ClientSession() as session:
        async with session.get(
            f"https://g.tenor.com/v1/random?q=Anime {method} GIF&key={get_api_key('tenor')}&limit=9"
        ) as response:
            data = await response.json()
            return choice(data["results"])["media"][0]["gif"]["url"]


async def construct_gif_embed(
    author: Union[User, Member],
    target: Union[User, Member],
    method: str,
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
        url=await get_gif_url(method)
    )
