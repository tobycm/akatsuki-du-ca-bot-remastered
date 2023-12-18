"""
Quote api backend functions.
"""

from dataclasses import dataclass
from random import choice
from time import time

from aiohttp import ClientSession


@dataclass
class Quote:
    quote: str
    author: str


global quotes
quotes: list[Quote] = []
global updated_at
updated_at = 0

global session
session: ClientSession | None = None


async def get_quote() -> Quote:
    """
    Return a random quote in dict.
    """

    global quotes
    global updated_at
    if int(time()) - updated_at > 600:
        global session

        if not session:
            session = ClientSession()

        async with session.get("https://zenquotes.io/api/quote/") as response:
            quotes = []
            for quote in await response.json():
                quotes.append(Quote(quote["q"], quote["a"]))
            updated_at = int(time())

    return choice(quotes)
