import json
from discord import Object, Interaction, app_commands, Intents, AllowedMentions
from discord.ext import commands

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.vault import get_token

bot = commands.Bot(command_prefix=commands.when_mentioned, intents = Intents.all())
tree = bot.tree

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx):
    print(get_token("guild_id"))
    await tree.sync(guild = Object(id = get_token("guild_id")))
    await ctx.send("Synced!")

    
@tree.command(guild = Object(id = get_token("guild_id")))
@app_commands.describe(text = "say what")
async def say(interaction: Interaction, text: str):
    await interaction.response.send_message(text, allowed_mentions = AllowedMentions.none())
    
bot.run(get_token("discord_token"))
