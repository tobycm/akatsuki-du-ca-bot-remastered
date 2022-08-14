"""
Quote api backend functions.
"""

from typing import List
from aiohttp import ClientSession


async def get_quotes() -> List[dict]:
    """
    Return a list of quotes in dict.
    """

    async with ClientSession() as session:
        async with session.get("https://zenquotes.io/api/quotes/") as response:
            data = await response.json()

            quotes = []

            for quote in data:
                quotes.append({quote["a"]: quote["q"]})

            return quotes
