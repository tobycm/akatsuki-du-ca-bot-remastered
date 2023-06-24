"""
Waifu API module
"""

from aiohttp import ClientSession
from waifuim import WaifuAioClient
from waifuim.types import Image

global waifuim


def load(session: ClientSession):
    global waifuim
    waifuim = WaifuAioClient(session=session)


async def random_image(nsfw: bool = False) -> Image:
    image = await waifuim.search(is_nsfw=nsfw)
    assert not isinstance(image, dict)
    if isinstance(image, list):
        image = image[0]

    return image
