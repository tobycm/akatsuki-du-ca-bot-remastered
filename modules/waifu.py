"""
Waifu API module
"""

from waifuim import WaifuAioClient
from waifuim.types import Image

waifuim = WaifuAioClient()


async def random_image(nsfw: bool = False) -> Image:
    image = await waifuim.search(is_nsfw=nsfw)
    assert not isinstance(image, dict)
    if isinstance(image, list):
        image = image[0]

    return image
