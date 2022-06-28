import discord
from discord.ext.commands import Context, Bot

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.vault import get_bot_config
from modules.database_utils import return_redis_instance, get_prefix
from modules.load_lang import get_lang

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ self-coded modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv bot settings

default_prefix = "$"

async def get_prefix_for_bot(bot, message):
    prefix = await get_prefix(bot.redis_ins, message.guild.id)
    if prefix is None:
        return default_prefix
    return prefix

bot = Bot(command_prefix=get_prefix_for_bot, activity=discord.Game(name="Hibiki Ban Mai"), intents = discord.Intents.all())
tree = bot.tree

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx : Context):
    await tree.sync(guild = discord.Object(id = get_bot_config("guild_id")))
    await ctx.send("Synced!")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name}")
    
@bot.event
async def on_guild_remove(guild):
    print(f"Left {guild.name}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ for events code
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

async def start_up():
    bot.redis_ins = return_redis_instance()
    bot.lang = await get_lang()
    
bot.setup_hook = start_up
    
bot.run(get_bot_config("discord_token"))
