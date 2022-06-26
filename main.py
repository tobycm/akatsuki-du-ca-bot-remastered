from discord import Object, Interaction, app_commands, Intents, AllowedMentions, Game
from discord.ext import commands

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.vault import get_token

bot = commands.Bot(command_prefix=commands.when_mentioned, activity=Game(name="Hibiki Ban Mai"), intents = Intents.all())
tree = bot.tree
bot.load_extension('jishaku')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx):
    print(get_token("guild_id"))
    await tree.sync(guild = Object(id = get_token("guild_id")))
    await ctx.send("Synced!")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code

@bot.event
async def on_guild_join(guild):
    print(f"Joined {guild.name}")
    # guild_create(guild.id, guild.name, guild.owner.id)
    
async def on_guild_remove(guild):
    print(f"Left {guild.name}")
    # guild_delete(guild.id)
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ for events code
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

bot.run(get_token("discord_token"))
