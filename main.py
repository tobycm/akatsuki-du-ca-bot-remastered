#!/usr/bin/env python3

"""
Main bot file.
"""

from discord import Game, Intents
from discord.ext.commands import Context

from models.bot_models import AkatsukiDuCa
from modules.checks_and_utils import check_owners, get_prefix_for_bot
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

    if not await check_owners(bot.redis_ins, ctx):
        return
    await tree.sync()
    await ctx.send("Synced!")


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ sync command
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

bot.run(get_bot_config("token"))
