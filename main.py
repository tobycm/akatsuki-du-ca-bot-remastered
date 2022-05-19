import discord
import json

bot = discord.Client(intents = discord.Intents.all())

with open("./config/settings.json", "r") as f:
    config = json.load(f)
    
bot.run(config["discord_token"])
