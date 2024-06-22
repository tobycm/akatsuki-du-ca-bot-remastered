#!/usr/bin/env python3
"""
Main bot file.
"""

import asyncio
import datetime
import traceback

from discord import Game, Guild, Intents, Interaction, Message
from discord.app_commands import errors as app_commands_errors
from discord.ext.commands import Context
from discord.ext.commands import errors as commands_errors

from akatsuki_du_ca import AkatsukiDuCa
from config import config
from modules import database, exceptions, lang, misc, osu
from modules.log import logger

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
    logger.info("Reloaded by command!")


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ bot commands
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

database.load(config.redis)
lang.load()
misc.load()


@bot.event
async def on_ready():
    """
    Run on ready (don't touch pls).
    """

    logger.info(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: Message):
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

    logger.info(f"Joined {guild.name}")


@bot.event
async def on_guild_remove(guild: Guild):
    """
    Run on guild remove.
    """

    logger.info(f"Left {guild.name}")


@bot.event
async def on_error(ctx: Context, error: Exception):
    """
    Command error handler
    """

    if isinstance(error, commands_errors.CommandNotFound):
        return

    _lang = await lang.get_lang(ctx.author.id)

    if isinstance(error, commands_errors.CommandOnCooldown):
        return await ctx.send(
            _lang("main.exceptions.command_on_cooldown") %
            round(error.retry_after, 1)
        )

    if isinstance(error, exceptions.LangNotAvailable):
        return await ctx.send(_lang("main.exceptions.language_not_available"))

    if isinstance(error, exceptions.MusicException.AuthorNotInVoice):
        return await ctx.send(_lang("music.voice_client.error.user_no_voice"))

    if isinstance(error, exceptions.MusicException.DifferentVoice):
        return await ctx.send(
            _lang("music.voice_client.error.playing_in_another_channel")
        )

    if isinstance(error, exceptions.MusicException.NoPermissionToConnect):
        return await ctx.send(_lang("music.voice_client.error.no_permission"))

    if isinstance(error, exceptions.MusicException.NotConnected):
        return await ctx.send(_lang("music.voice_client.error.not_connected"))

    if isinstance(error, exceptions.MusicException.NotPlaying):
        return await ctx.send(_lang("music.misc.action.error.no_music"))

    if isinstance(error, exceptions.MusicException.QueueEmpty):
        return await ctx.send(_lang("music.misc.action.error.no_queue"))

    if isinstance(error, exceptions.MusicException.TrackNotFound):
        return await ctx.send(_lang("music.voice_client.error.not_found"))

    # send error to channel
    error_channel = bot.get_channel(config.bot.channels.error)
    assert error_channel
    assert isinstance(error_channel, misc.TextableChannel)

    await error_channel.send(
        f"```py\n{''.join(traceback.format_exception(error))}\n```"
    )

    await ctx.send(_lang("main.exceptions.unknown"))

    # throw again
    raise error


@bot.tree.error
async def on_error(interaction: Interaction, error):
    """
    Command error handler
    """

    if isinstance(error, app_commands_errors.CommandNotFound):
        return

    _lang = await lang.get_lang(interaction.user.id)

    if isinstance(error, app_commands_errors.CommandOnCooldown):
        return await interaction.edit_original_response(
            content = _lang("main.exceptions.command_on_cooldown") %
            round(error.retry_after, 1)
        )

    if isinstance(error, exceptions.LangNotAvailable):
        return await interaction.edit_original_response(
            content = _lang("main.exceptions.language_not_available")
        )

    if isinstance(error, exceptions.MusicException.AuthorNotInVoice):
        return await interaction.edit_original_response(
            content = _lang("music.voice_client.error.user_no_voice")
        )

    if isinstance(error, exceptions.MusicException.DifferentVoice):
        return await interaction.edit_original_response(
            content = _lang(
                "music.voice_client.error.playing_in_another_channel"
            )
        )

    if isinstance(error, exceptions.MusicException.NoPermissionToConnect):
        return await interaction.edit_original_response(
            content = _lang("music.voice_client.error.no_permission")
        )

    if isinstance(error, exceptions.MusicException.NotConnected):
        return await interaction.edit_original_response(
            content = _lang("music.voice_client.error.not_connected")
        )

    if isinstance(error, exceptions.MusicException.NotPlaying):
        return await interaction.edit_original_response(
            content = _lang("music.misc.action.error.no_music")
        )

    if isinstance(error, exceptions.MusicException.QueueEmpty):
        return await interaction.edit_original_response(
            content = _lang("music.misc.action.error.no_queue")
        )

    if isinstance(error, exceptions.MusicException.TrackNotFound):
        return await interaction.edit_original_response(
            content = _lang("music.voice_client.error.not_found")
        )

    # send error to channel
    error_channel = bot.get_channel(config.bot.channels.error)
    assert error_channel
    assert isinstance(error_channel, misc.TextableChannel)

    error_code = f"{datetime.datetime.now()} {interaction.command.name} {interaction.guild_id} {interaction.user.id} {type(error).__name__} {misc.random_string(8)}"

    await error_channel.send(
        f"Error code: `{error_code}`\n" +
        f"```py\n{''.join(traceback.format_exception(error))}\n```"
    )

    await interaction.edit_original_response(
        content = f"Error code: `{error_code}`\n" +
        _lang("main.exceptions.unknown")
    )

    # throw again
    raise error


async def setup_hook():
    """
    Run on startup (yes you can touch this).
    """

    await bot.load_extension("cogs")
    await bot.load_extension("api")
    await bot.load_extension("jishaku")
    logger.info("Loaded jishaku")

    await osu.load(config.api.osu.key)


setattr(bot, "setup_hook", setup_hook)

bot.run(config.bot.token)


async def cleanup():
    await bot.session.close()
    await database.cleanup()


asyncio.run(cleanup())
