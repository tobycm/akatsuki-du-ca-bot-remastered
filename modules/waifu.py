"""
Waifu API module
"""

from aiohttp import ClientSession
from waifuim import WaifuAioClient
from waifuim.types import Image

global waifuim
waifuim: WaifuAioClient | None = None


async def random_image(nsfw: bool = False) -> Image:
    global waifuim

    if not waifuim:
        waifuim = WaifuAioClient()

    image = await waifuim.search(is_nsfw = nsfw)
    assert not isinstance(image, dict)
    if isinstance(image, list):
        image = image[0]

    return image
