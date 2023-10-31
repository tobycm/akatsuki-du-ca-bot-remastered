"""
GIF backend functions.
"""

from random import choice

from aiohttp import ClientSession

Url = str

global session
session: ClientSession


def load(sess: ClientSession):
    global session
    session = sess


async def get_gif_url(action: str, api_key: str) -> Url:
    """
    Get a GIF url using search query
    """

    async with session.get(
        f"https://g.tenor.com/v1/random?q=Anime {action} GIF&key={api_key}&limit=9"
    ) as response:
        return choice((await
                       response.json())["results"])["media"][0]["gif"]["url"]
