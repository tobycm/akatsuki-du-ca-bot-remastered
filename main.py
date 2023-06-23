#!/usr/bin/env python3

"""
Main bot file.
"""

import asyncio

from discord import Game, Guild, Intents, Message
from discord.ext.commands import Context

from api import Routes
from models.bot_models import AkatsukiDuCa
from modules import database, lang, osu, vault
from modules.checks_and_utils import check_owners, get_prefix_for_bot

bot = AkatsukiDuCa(
    command_prefix=get_prefix_for_bot,
    activity=Game(name="Hibiki Ban Mai"),
    intents=Intents.all(),
    help_command=None,
)


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
    await bot.tree.sync()
    await ctx.send("Synced!")


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

bot.config = vault.load()
database.load(bot.config.redis)
lang.load()
osu.load(bot.config.api_keys.osu)


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

    assert bot.user
    if message.content == f"<@{bot.user.id}>":
        prefix = await get_prefix_for_bot(bot, message)
        await message.reply(
            prefix.join((await lang.get_lang(message.author.id))("main.PingForPrefix"))
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

    await bot.load_extension("cogs")
    await bot.load_extension("api")
    await bot.load_extension("jishaku")
    bot.logger.info("Loaded jishaku")


bot.setup_hook = setup_hook

bot.run(bot.config.token)


async def cleanup():
    await osu.cleanup()
    await database.cleanup()


asyncio.run(cleanup())
