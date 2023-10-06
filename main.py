#!/usr/bin/env python3
"""
Main bot file.
"""

import asyncio

from discord import Game, Guild, Intents, Message, TextChannel
from discord.ext.commands import Context

from akatsuki_du_ca import AkatsukiDuCa
from config import config
from modules import database, gif, lang, minecraft, misc, osu, quote, waifu

bot = AkatsukiDuCa(
    command_prefix = misc.get_prefix_for_bot,
    activity = Game(name = "Hibiki Ban Mai"),
    intents = Intents.all(),
    help_command = None,
)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot settings
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv bot commands


@bot.command(name = "sc", hidden = True)
async def sync_command(ctx: Context):
    """
    Sync commands to global.
    """

    if not await misc.check_owners(ctx):
        return
    await bot.tree.sync()
    await ctx.send("Synced!")


@bot.command(name = "reload", hidden = True)
async def reload(ctx: Context):
    """
    Reload bot.
    """

    if not await misc.check_owners(ctx):
        return

    await bot.reload_extension("cogs")
    await bot.reload_extension("api")
    await bot.reload_extension("jishaku")
    await ctx.send("Reloaded!")
    bot.logger.info("Reloaded by command!")


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot commands
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

database.load(config.redis)
lang.load()
osu.load(config.api.osu.key, bot.session)
minecraft.load(bot.session)
waifu.load(bot.session)
quote.load(bot.session)
gif.load(bot.session)
misc.load()


@bot.event
async def on_ready():
    """
    Run on ready (don't touch pls).
    """

    bot.logger.info(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: Message): # pylint: disable=arguments-differ
    """
    Run on new message.
    """

    if message.author.bot:
        return

    assert bot.user
    if message.content == f"<@{bot.user.id}>":
        prefix = await misc.get_prefix_for_bot(bot, message)
        await message.reply(
            (await lang.get_lang(message.author.id
                                 ))("main.exceptions.ping_for_prefix") % prefix
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


@bot.event
async def on_command_error(ctx: Context, error: Exception):
    """
    Command error handler
    """

    # send error to channel
    error_channel = bot.get_channel(config.bot.channels.error)
    assert isinstance(error_channel, TextChannel)

    await error_channel.send(f"```py\n{error}\n```")

    # throw again
    raise error


async def setup_hook():
    """
    Run on startup (yes you can touch this).
    """

    await bot.load_extension("cogs")
    await bot.load_extension("api")
    await bot.load_extension("jishaku")
    bot.logger.info("Loaded jishaku")


setattr(bot, "setup_hook", setup_hook)

bot.run(config.bot.token)


async def cleanup():
    await bot.session.close()
    await database.cleanup()


asyncio.run(cleanup())
