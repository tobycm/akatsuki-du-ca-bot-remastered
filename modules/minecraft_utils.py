from discord import Embed
from aiohttp import ClientSession

async def get_minecraft_user_embed(username : str, lang : dict) -> Embed:
    async with ClientSession() as session:
        async with session.get("https://playerdb.co/api/player/minecraft/" + username) as r:
            data = await r.json()
            
            uuid = data["data"]["player"]["id"]
            image = f"https://crafatar.com/renders/body/{uuid}"
            thumbnail = f"https://crafatar.com/avatars/{uuid}"
            
            embed = Embed(title = lang["MinecraftAccount"][0] + username, description = lang["MinecraftAccount"][1] + username)
            embed.set_image(url = image)
            embed.set_thumbnail(url = thumbnail)
            return embed

async def get_minecraft_server_info_embed(server_ip : str, lang : dict) -> Embed:
    async with ClientSession() as session:
        async with session.get("https://api.mcsrvstat.us/2/" + server_ip) as r:
            data = await r.json()
            
            if data["online"] == "false":
                return Embed(title = server_ip + lang["MinecraftServer"][0], description = lang["MinecraftServer"][2] + server_ip)
            return Embed(title = server_ip + lang["MinecraftServer"][1], description = lang["MinecraftServer"][2] + server_ip + "\n" + lang["MinecraftServer"][3] % (r["players"]["online"]))