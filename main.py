from time import time
import logging
from discord import Game, Intents
from discord.ext.commands import Context, Bot

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.checks_and_utils import check_owners
from modules.log_utils import command_log
from modules.quote_api import get_quotes
from modules.vault import get_bot_config
from modules.database_utils import return_redis_instance, get_prefix
from modules.load_lang import get_lang

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ self-coded modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv cog import

from cogs.fun import FunCog, GIFCog
from cogs.music import RadioMusic
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import UtilsCog, MinecraftCog
from cogs.admin import PrefixCog, BotAdminCog

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ cog import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv bot settings

DEFAULT_PREFIX = get_bot_config("prefix")

async def get_prefix_for_bot(bot, message):
    prefix = await get_prefix(bot.redis_ins, message.guild.id)
    if prefix is None:
        return DEFAULT_PREFIX
    return prefix

bot = Bot(
    command_prefix = get_prefix_for_bot,
    activity = Game(name="Hibiki Ban Mai"),
    intents = Intents.all()
         )
tree = bot.tree

bot_logger = logging.getLogger('discord')

@bot.event
async def on_ready():
    bot_logger.info(f"Logged in as {bot.user}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command
    
@bot.command(name = "sc", hidden = True)
async def sc(ctx : Context):
    command_log(ctx.author.id, ctx.guild.id, ctx.channel.id, "sc")
    if not await check_owners(bot.redis_ins, ctx):
        return
    await tree.sync()
    await ctx.send("Synced!")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code

@bot.event
async def on_guild_join(guild):
    bot_logger.info(f"Joined {guild.name}")
    
@bot.event
async def on_guild_remove(guild):
    bot_logger.info(f"Left {guild.name}")
    
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ for events code
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

async def start_up():
    bot.redis_ins = return_redis_instance()
    bot.lang = await get_lang()
    bot.quotes = await get_quotes()
    bot.quotes_added = time()
    
    await bot.load_extension('jishaku')
    bot_logger.info("Loaded jishaku")
    
    await bot.add_cog(FunCog(bot))
    await bot.add_cog(GIFCog(bot))
    bot_logger.info("-> Fun and GIF Cog added <-")
    await bot.add_cog(RadioMusic(bot))
    bot_logger.info(" -> Radio music cog added <-")
    await bot.add_cog(NSFWCog(bot))
    bot_logger.info(" -> NSFW cog added <-")
    await bot.add_cog(ToysCog(bot))
    bot_logger.info(" -> Toys cog added <-")
    await bot.add_cog(UtilsCog(bot))
    await bot.add_cog(MinecraftCog(bot))
    bot_logger.info(" -> Utils and Minecraft cog added <-")
    await bot.add_cog(PrefixCog(bot))
    bot_logger.info(" -> Prefix cog added <-")
    await bot.add_cog(BotAdminCog(bot))
    bot_logger.info(" -> Bot admin cog added <-")

bot.setup_hook = start_up
    
bot.run(get_bot_config("token"))
