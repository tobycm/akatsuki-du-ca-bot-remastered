import discord
from discord import app_commands
import json

# ----------------------------------------------------------------------------------------------------------------------

from cogs.fun import fun

# ----------------------------------------------------------------------------------------------------------------------

from modules.gifapi import getgif

bot = discord.Client(intents = discord.Intents.all())
botcommands = app_commands.CommandTree(bot)

bot.add(fun)

with open("./config/settings.json", "r") as f:
    config = json.load(f)
    
bot.run(config["discord_token"])
