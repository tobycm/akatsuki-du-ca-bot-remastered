"""
Main bot file.
"""

import logging
from discord import Game, Intents, Message
from discord.ext.commands import Context
from discord.ui import View

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ other modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv self-coded modules import

from modules.checks_and_utils import check_owners, return_user_lang
from modules.log_utils import command_log
from modules.quote_api import get_quotes
from modules.vault import get_bot_config
from modules.database_utils import get_user_lang, get_prefix

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ self-coded modules import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv models import

from models.main_models import LangSel
from models.bot_models import CustomBot

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ models import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv cog import

from cogs.fun import FunCog, GIFCog
from cogs.music import RadioMusic, MusicCog
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import UtilsCog, MinecraftCog
from cogs.admin import PrefixCog, BotAdminCog
from cogs.legacy_commands import LegacyCommands

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ cog import
# -------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv bot settings

DEFAULT_PREFIX = get_bot_config("prefix")


async def get_prefix_for_bot(bot: CustomBot, message: Message):  # pylint: disable=redefined-outer-name
    """
    Return the prefix for the bot.
    """

    prefix = await get_prefix(bot.redis_ins, message.guild.id)
    if prefix is None:
        return DEFAULT_PREFIX
    return prefix

bot = CustomBot(
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
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv before command run

async def check_lang(message: Message):
    """
    First time use bot so check lang
    """
    print("here")
    if await get_user_lang(bot.redis_ins, message.author.id) is not None:
        print("here")
        return True
    print("here")
    select_menu = LangSel(bot.lang)
    view = View(timeout=45)
    for lang in bot.lang:
        for lang_name, _ in lang:
            select_menu.add_option(label=lang_name, value=lang_name)
    view.add_item(select_menu)
    print("here")

    print("here")
    await message.reply(
        content="Có vẻ như đây là lần đầu bạn sử dụng bot này, mình sẽ giúp bạn cài đặt ngôn ngữ cho bạn.\n Looks like this is your first time using this bot, I will help you to set up your language.",
        view=view
    )
    return False

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ before command run
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv for events code


@bot.event
async def on_message(message: Message):
    """
    Run on new message.
    """

    if message.author.bot:
        return

    if not await check_lang(message):
        return

    if message.content == f"<@{bot.user.id}>":
        lang = await return_user_lang(bot, message.author.id)
        prefix = await get_prefix(bot.redis_ins, message.guild.id)
        await message.reply(
            lang["main"]["PingForPrefix"][0] + prefix + lang["main"]["PingForPrefix"][1]
        )

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

    bot.quotes = await get_quotes()

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
    await bot.add_cog(LegacyCommands(bot))
    bot_logger.info(" -> Toby sus cog added <-")

bot.setup_hook = start_up

bot.run(get_bot_config("token"))
