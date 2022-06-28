from typing import List
from aiohttp import ClientSession

async def get_quotes() -> List([dict]):
    async with ClientSession() as session:
        async with session.get("https://zenquotes.io/api/quotes/") as r:
            data = await r.json()

            quotes = []
            
            for quote in data:
                quotes.append({quote["a"]: quote["q"]})

            return quotes