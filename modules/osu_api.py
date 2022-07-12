import json
from aiohttp import ClientSession
from modules.vault import get_bot_config

API_ENDPOINT = "https://osu.ppy.sh/api/"

async def get_osu_user_info(user : str) -> json:
    async with ClientSession() as session:
        async with session.get(f"{API_ENDPOINT}get_user?k={get_bot_config('osu_token')}&u={user}") as r:
            if r.text == "[]":
                return None
            data = await r.json()
            data = data[0]
            total_playcount = int(data["count300"]) + int(data["count100"]) + int(data["count50"])

            new_data = {
                "username": data["username"],
                "user_id": data["user_id"],
                "join_date": data["join_date"],
                "total_playcount": total_playcount,
                "total_score": data["total_score"],
                "global_rank": data["pp_rank"],
                "level": data["level"],
                "pp": data["pp_raw"],
                "accuracy": data["accuracy"],
                "SS": data["count_rank_ss"],
                "S": data["count_rank_s"],
                "A": data["count_rank_a"],
                "country": data["country"].lower(),
                "total_seconds_played": data["total_seconds_played"],
                "country_rank": data["pp_country_rank"],
            }
            return new_data
