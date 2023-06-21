#!/usr/bin/env python3

"""
Main bot file.
"""

from discord import Game, Guild, Intents, Message
from discord.ext.commands import Context

from api.ipc import Routes
from cogs.admin import BotAdminCog, PrefixCog
from cogs.fun import FunCog, GIFCog
from cogs.legacy_commands import LegacyCommands
from cogs.music import MusicCog, RadioMusic
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import MinecraftCog, UtilsCog
from models.bot_models import AkatsukiDuCa
from modules.checks_and_utils import check_owners, get_prefix_for_bot
from modules.database_utils import get_user_lang
from modules.lang import lang
from modules.quote_api import get_quotes
from modules.vault import get_bot_config

bot = AkatsukiDuCa(
    command_prefix=get_prefix_for_bot,
    activity=Game(name="Hibiki Ban Mai"),
    intents=Intents.all(),
    help_command=None,
)
tree = bot.tree

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv sync command


@bot.command(name="sc", hidden=True)
async def sync_command(ctx: Context):
    """
    Sync commands to global.
    """

    if not await check_owners(ctx):
        return
    await tree.sync()
    await ctx.send("Synced!")


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot


@bot.event
async def on_ready():
    """
    Run on ready (don't touch pls).
    """

    bot.logger.info(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: Message):  # pylint: disable=arguments-differ
    """
    Run on new message.
    """

    if message.author.bot:
        return

    if message.content == f"<@{bot.user.id}>":
        prefix = await get_prefix_for_bot(bot, message)
        await message.reply(
            prefix.join(
                lang("main.PingForPrefix", await get_user_lang(message.author.id))
            )
        )

    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild: Guild):
    """
    Run on guild join.
    """

    bot.logger.info(f"Joined {guild.name}")


@bot.event
async def on_guild_remove(guild: Guild):
    """
    Run on guild remove.
    """

    bot.logger.info(f"Left {guild.name}")


async def setup_hook():
    """
    Run on startup (yes you can touch this).
    """

    bot.quotes = await get_quotes()

    # add ipc routes
    await bot.add_cog(Routes(bot))

    for cog in (
        FunCog,
        GIFCog,
        RadioMusic,
        MusicCog,
        NSFWCog,
        ToysCog,
        UtilsCog,
        MinecraftCog,
        PrefixCog,
        BotAdminCog,
        LegacyCommands,
    ):
        await bot.add_cog(cog(bot))

    await bot.load_extension("jishaku")
    bot.logger.info("Loaded jishaku")


bot.setup_hook = setup_hook

bot.run(get_bot_config("token"))
