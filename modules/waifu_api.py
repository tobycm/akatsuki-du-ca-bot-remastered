from typing import Tuple
from aiohttp import ClientSession
from random import choice

async def get_waifu_image_url() -> Tuple((1, 2)):
    url = f"https://api.waifu.im/random/?selected_tags={choice(['waifu', 'maid', 'uniform', 'marin-kitagawa', 'mori-calliope', 'raiden-shogun', 'oppai', 'selfies'])}"
    async with ClientSession() as session:
        async with session.get(url) as r:
            data = r.json()
            
    if data["images"]:
        url = data["images"][0]["url"]
        source = data["images"][0]["source"]
        
    return (url, source)
