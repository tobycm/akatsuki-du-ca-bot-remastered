import discord
from discord.ext import commands

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.vault import get_bot_config
from modules.databaseutils import *

bot = commands.Bot(command_prefix=commands.when_mentioned, activity=discord.Game(name="Hibiki Ban Mai"), intents = discord.Intents.all())
tree = bot.tree

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx):
    print(get_bot_config("guild_id"))
    await tree.sync(guild = discord.Object(id = get_bot_config("guild_id")))
    await ctx.send("Synced!")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name}")
    # guild_create(guild.id, guild.name, guild.owner.id)
    
@bot.event
async def on_guild_remove(guild):
    print(f"Left {guild.name}")
    # guild_delete(guild.id)
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ for events code
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

async def start_up():
    await bot.wait_until_ready()
    
    bot.redis_ins = return_redis_instance()
    await bot.load_extension('jishaku')
    
bot.run(get_bot_config("discord_token"))
