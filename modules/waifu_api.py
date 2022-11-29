"""
Waifu APi backend functions.
"""
from aiohttp import ClientSession

from models.waifuim_models import Image

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
        image = Image(data["images"][0])

    return (image.url, image.source)
