import discord
import requests

def getgif(self, apikey : str, method : str, username : str, target : discord.User, lang):

    if target.id == self.bot.user.id:
        return discord.Embed(description="etou...")

    r = requests.get("https://g.tenor.com/v1/random?q=%s&key=%s&limit=1" % (f"Anime {method} GIF", apikey))
    r = r.json()

    url = r['results'][0]["media"][0]["gif"]["url"]
    title = lang["GIF"][method]["title"]
    mid_text = lang["GIF"][method]["mid_text"]
    mid_text_2 = lang["GIF"][method]["mid_text_2"]

    if method == "slap":
        desc = str(target) + mid_text + username
    else:
        desc = username + mid_text + str(target)

    if method in ["hug", "kick", "poke", "bite", "cuddle"]:
        desc += mid_text_2

    embed = discord.Embed(title=title, description=desc)
    embed.set_image(url=url)
    return embed
