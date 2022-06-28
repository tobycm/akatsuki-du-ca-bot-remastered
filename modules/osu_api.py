import json
from aiohttp import ClientSession
from vault import get_bot_config

API_ENDPOINT = "https://osu.ppy.sh/api/v2/"

async def get_osu_user_info(user : str) -> json:
    async with ClientSession() as session:
        async with session.get(f"{API_ENDPOINT}get_user?k={get_bot_config('osu_token')}&u={user}") as r:
            data = await r.json()
            return data
