import discord
from discord.ext import commands
from discord import AllowedMentions, app_commands
import json

bot = commands.Bot(command_prefix=commands.when_mentioned, intents = discord.Intents.all())
tree = bot.tree

with open("./config/settings.json", "r") as f:
    config = json.load(f)
    
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx):
    print(config["guild_id"])
    await tree.sync(guild = discord.Object(id = config["guild_id"]))
    await ctx.send("Synced!")

    
@tree.command(guild = discord.Object(id = config["guild_id"]))
@app_commands.describe(text = "say what")
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text, allowed_mentions = AllowedMentions.none())
    
bot.run(config["discord_token"])
