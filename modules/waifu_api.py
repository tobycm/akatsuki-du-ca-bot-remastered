"""
Waifu APi backend functions.
"""
from aiohttp import ClientSession

async def get_waifu_image_url() -> tuple(("url", "source")):
    """
    Get a random waifu image url and source.
    """

    async with ClientSession() as session:
        async with session.get(
            "https://api.waifu.im/search"
        ) as response:
            data = await response.json()

    if data["images"]:
        url = data["images"][0]["url"]
        source = data["images"][0]["source"]

    return (url, source)
