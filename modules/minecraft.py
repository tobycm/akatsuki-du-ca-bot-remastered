from discord import Embed
import aiohttp
import json

def get_minecraft_user(username, lang):
    r = requests.get("https://playerdb.co/api/player/minecraft/" + username)
    r = json.loads(r.text)
    uuid = r["data"]["player"]["id"]
    image = f"https://crafatar.com/renders/body/{uuid}"
    thumbnail = f"https://crafatar.com/avatars/{uuid}"
    embed = Embed(title=lang["MinecraftAccount"][0] + username, description=lang["MinecraftAccount"][1] + username)
    embed.set_image(url = image)
    embed.set_thumbnail(url = thumbnail)
    return embed

def get_minecraft_server_info(server_ip, lang):
    api = "https://api.mcsrvstat.us/2/"
    r = requests.get(api + server_ip)
    r = json.loads(r.text)
    if r["online"] == "false":
        return Embed(title=server_ip + lang["MinecraftServer"][0], description=lang["MinecraftServer"][2] + server_ip)
    return Embed(title=server_ip + lang["MinecraftServer"][1], description=lang["MinecraftServer"][2] + server_ip + "\n" + lang["MinecraftServer"][3] % (r["players"]["online"]))