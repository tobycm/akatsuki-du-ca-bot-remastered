import aiohttp
from random import random
from discord import Embed
from modules.vault import get_bot_config

async def get_gif_url(method : str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://g.tenor.com/v1/random?q=Anime {method} GIF&key={get_bot_config('tenor_token')}&limit=1") as r:
            data = await r.json()
            return data["results"][random(0, len(data["result"]))]["media"][0]["gif"]["url"]
    
async def construct_gif_embed(author : str, target : str, method : str, lang : dict):
    title = lang["GIF"][method]["title"]
    
    if method == "slap":
        desc = f"{target} {lang['GIF'][method]['mid_text']} {author}"
    else:
        desc = str(author) + lang["GIF"][method]["mid_text"] + str(target)

    if method in ["hug", "kick", "poke", "bite", "cuddle"]:
        desc = desc + lang["GIF"][method]["mid_text_2"]
        
    embed = Embed(title = title, description = desc)
    embed.set_image(url = get_gif_url(method))