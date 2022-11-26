"""
NSFW backend functions for NSFW cog.
"""

from aiohttp import ClientSession


async def get_nsfw() -> tuple(("url", "source")):
    """
    Return a random NSFW image url and source.
    """

    async with ClientSession() as session:
        async with session.get(
            "https://api.waifu.im/search?is_nsfw=true"
        ) as response:
            data = await response.json()

    if data["images"]:
        url = data["images"][0]["url"]
        source = data["images"][0]["source"]

    return (url, source)
