from io import BytesIO
from base64 import b64decode
from discord import Embed
from aiohttp import ClientSession

async def get_minecraft_user_embed(username : str) -> tuple(["uuid", "image", "thumbnail"]):
    async with ClientSession() as session:
        async with session.get("https://playerdb.co/api/player/minecraft/" + username) as r:
            data = await r.json()
            
            uuid = data["data"]["player"]["id"]
            image = f"https://crafatar.com/renders/body/{uuid}"
            thumbnail = f"https://crafatar.com/avatars/{uuid}"

            return (uuid, image, thumbnail)

async def get_minecraft_server_info(server_ip : str) -> Embed:
    async with ClientSession() as session:
        async with session.get("https://api.mcsrvstat.us/2/" + server_ip) as r:
            data = await r.json()
            
            if data["online"] == "false":
                return "not online"
            return {
                "motd": data["motd"]["clean"],
                "players": [data["players"]["online"], data["players"]["max"]],
                "version": data["version"],
                "icon": data["icon"].replace('\\', '')
            }