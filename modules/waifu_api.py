"""
Waifu APi backend functions.
"""
from random import choice
from aiohttp import ClientSession

async def get_waifu_image_url() -> tuple(("url", "source")):
    """
    Get a random waifu image url and source.
    """

    cate = choice(
        [
            'waifu',
            'maid',
            'uniform',
            'marin-kitagawa',
            'mori-calliope',
            'raiden-shogun',
            'oppai',
            'selfies'
        ]
    )
    url = f"https://api.waifu.im/random/?selected_tags={cate}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = response.json()

    if data["images"]:
        url = data["images"][0]["url"]
        source = data["images"][0]["source"]

    return (url, source)
