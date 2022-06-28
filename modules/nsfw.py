from typing import Tuple
from aiohttp import ClientSession
from random import choice
        
async def get_nsfw() -> Tuple("url", "source"):
    async with ClientSession() as session:
        async with session.get(f"https://api.waifu.im/random/?selected_tags={choice(['ass', 'ero', 'hentai', 'milf', 'oral', 'paizuri', 'ecchi'])}") as r:
            data = await r.json()

            if data["images"]:
                return (data["images"][0]["url"], data["images"][0]["source"])