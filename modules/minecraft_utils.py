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

async def get_minecraft_server_info_embed(server_ip : str, lang : dict) -> Embed:
    async with ClientSession() as session:
        async with session.get("https://api.mcsrvstat.us/2/" + server_ip) as r:
            data = await r.json()
            
            if data["online"] == "false":
                return "not online"
            return {
                "motd": data["motd"]["raw"],
                "players": [data["players"]["online"], data["players"]["max"]],
                "version": data["version"],
                "online": data["online"],
                "hostname": data["hostname"],
                "icon": BytesIO(b64decode(data["icon"].replace('\\', '')))
            }