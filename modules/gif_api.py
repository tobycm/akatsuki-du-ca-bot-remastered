"""
GIF backend functions.
"""

from random import choice

from aiohttp import ClientSession
from discord import Embed

from modules.lang import get_lang_by_address
from modules.vault import get_api_key


async def get_gif_url(method: str) -> str("url"):
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
    author: str, target: str, method: str, lang: dict
) -> Embed:
    """
    Construct a GIF embed
    """

    mid_text = get_lang_by_address(f"gif.{method}.mid_text", lang)

    if method == "slap":
        description = f"{target} {mid_text} {author}"
    else:
        description = f"{author} {mid_text} {target}"
    if method in ["hug", "kick", "poke", "bite", "cuddle"]:
        description += get_lang_by_address(f"gif.{method}.mid_text_2", lang)  # type: ignore

    return Embed(
        title=get_lang_by_address(f"gif.{method}.title", lang), description=description
    ).set_image(url=await get_gif_url(method))
