"""
Main bot file.
"""

from time import time
import logging
from discord import Game, Intents, Message
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
from cogs.music import RadioMusic, MusicCog
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import UtilsCog, MinecraftCog
from cogs.admin import PrefixCog, BotAdminCog

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ cog import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv bot settings

DEFAULT_PREFIX = get_bot_config("prefix")


async def get_prefix_for_bot(bot: Bot, message: Message): # pylint: disable=redefined-outer-name
    """
    Return the prefix for the bot.
    """

    prefix = await get_prefix(bot.redis_ins, message.guild.id)
    if prefix is None:
        return DEFAULT_PREFIX
    return prefix

bot = Bot(
    command_prefix=get_prefix_for_bot,
    activity=Game(name="Hibiki Ban Mai"),
    intents=Intents.all(),
    help_command=None
)
tree = bot.tree

bot_logger = logging.getLogger('discord')
logging.basicConfig(
    filename="log/full_bot_log.txt",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)


@bot.event
async def on_ready():
    """
    Run on ready (don't touch pls).
    """

    bot_logger.info(f"Logged in as {bot.user}")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command


@bot.command(name="sc", hidden=True)
@command_log
async def sync_command(ctx: Context):
    """
    Sync commands to global.
    """

    if not await check_owners(bot.redis_ins, ctx):
        return
    await tree.sync()
    await ctx.send("Synced!")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code


@bot.event
async def on_message(message: Message):
    """
    Run on new message.
    """

    if message.author.bot:
        return

    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    """
    Run on guild join.
    """

    bot_logger.info(f"Joined {guild.name}")


@bot.event
async def on_guild_remove(guild):
    """
    Run on guild leave.
    """

    bot_logger.info(f"Left {guild.name}")

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ for events code
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot


async def start_up():
    """
    Run on startup (yes you can touch this).
    """

    bot.redis_ins = return_redis_instance()
    bot.lang = get_lang()
    bot.quotes = await get_quotes()
    bot.quotes_added = time()

    await bot.load_extension('jishaku')
    bot_logger.info("Loaded jishaku")

    await bot.add_cog(FunCog(bot))
    await bot.add_cog(GIFCog(bot))
    bot_logger.info("-> Fun and GIF Cog added <-")
    await bot.add_cog(RadioMusic(bot))
    await bot.add_cog(MusicCog(bot))
    bot_logger.info(" -> Radio and Music cog added <-")
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
