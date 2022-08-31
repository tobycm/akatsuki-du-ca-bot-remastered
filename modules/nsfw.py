"""
NSFW backend functions for NSFW cog.
"""

from random import choice
from aiohttp import ClientSession


async def get_nsfw() -> tuple(("url", "source")):
    """
    Return a random NSFW image url and source.
    """

    cate = choice(['ass', 'ero', 'hentai', 'milf', 'oral', 'paizuri', 'ecchi'])

    async with ClientSession() as session:
        async with session.get(
            f"https://api.waifu.im/random/?selected_tags={cate}"
        ) as response:
            data = await response.json()

            if data["images"]:
                return (data["images"][0]["url"], data["images"][0]["source"])
