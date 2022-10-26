#!/usr/bin/env python3

"""
Main bot file.
"""

from discord import Game, Intents
from discord.ext.commands import Context

from modules.checks_and_utils import check_owners, get_prefix_for_bot
from modules.vault import get_bot_config

from models.bot_models import CustomBot

bot = CustomBot(
    command_prefix=get_prefix_for_bot,
    activity=Game(name="Hibiki Ban Mai"),
    intents=Intents.all(),
    help_command=None
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
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv before command run

# async def check_lang(message: Message):
#     """
#     First time use bot so check lang
#     """
#     print("here")
#     if await get_user_lang(bot.redis_ins, message.author.id) is not None:
#         print("here")
#         return True
#     print("here")
#     select_menu = LangSel(bot.lang)
#     view = View(timeout=45)
#     for lang in bot.lang:
#         for lang_name, _ in lang:
#             select_menu.add_option(label=lang_name, value=lang_name)
#     view.add_item(select_menu)
#     print("here")

#     print("here")
#     await message.reply(
#         content="Có vẻ như đây là lần đầu bạn sử dụng bot này, " +
#                 "mình sẽ giúp bạn cài đặt ngôn ngữ cho bạn.\n" +
#                 "Looks like this is your first time using this bot, " +
#                 "I will help you to set up your language.",
#         view=view
#     )
#     return False

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ before command run
# -----------------------------------------------------
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv assembling bot

bot.run(get_bot_config("token"))
