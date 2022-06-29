from aiohttp import ClientSession
from random import choice
from discord import Embed, User
from modules.vault import get_bot_config

async def get_gif_url(method : str) -> str("url"):
    async with ClientSession() as session:
        async with session.get(f"https://g.tenor.com/v1/random?q=Anime {method} GIF&key={get_bot_config('tenor_token')}&limit=10") as r:
            data = await r.json()
            return choice(data["results"])["media"][0]["gif"]["url"]
    
async def construct_gif_embed(author : str, target : str, method : str, lang : dict) -> Embed:
    title = lang[method]["title"]
    
    if method == "slap":
        desc = f"{target} {lang[method]['mid_text']} {author}"
    else:
        desc = f"{author} {lang[method]['mid_text']} {target}"
    if method in ["hug", "kick", "poke", "bite", "cuddle"]:
        desc = desc + lang[method]["mid_text_2"]
        
    embed = Embed(title = title, description = desc)
    embed.set_image(url = await get_gif_url(method))
    return embed