"""
Custom bot model
"""

import logging
from time import time
from typing import List
from aioredis import Redis
from discord import Intents, Message, Guild
from discord.ext.commands import Bot
from discord.ext.ipc.server import Server

from modules.database_utils import get_user_lang, return_redis_instance
from modules.load_lang import get_lang
from modules.quote_api import get_quotes
from modules.checks_and_utils import get_prefix_for_bot

from cogs.fun import FunCog, GIFCog
from cogs.music import RadioMusic, MusicCog
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import UtilsCog, MinecraftCog
from cogs.admin import PrefixCog, BotAdminCog
from cogs.legacy_commands import LegacyCommands

from api.ipc import Routes

COGS = (
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
    LegacyCommands
)

class CustomBot(Bot):
    """
    Custom bot class
    """

    def __init__(self, *args, intents=Intents.all(), **kwargs):
        super().__init__(*args, intents=intents, **kwargs)

    redis_ins: Redis = return_redis_instance()
    lang: dict = get_lang()
    quotes: List[dict]
    quotes_added: float = time()
    logger: logging.Logger = logging.getLogger('discord')
    ipc: Server

    logging.basicConfig(
        filename="log/full_bot_log.txt",
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )

    async def on_ready(self):
        """
        Run on ready (don't touch pls).
        """

        self.logger.info(f"Logged in as {self.user}")

    async def on_message(self, message: Message): # pylint: disable=arguments-differ
        """
        Run on new message.
        """

        if message.author.bot:
            return

        if message.content == f"<@{self.user.id}>":
            lang_option = await get_user_lang(self.redis_ins, message.author.id)
            lang = self.lang.get(lang_option if lang_option else "en-us")
            prefix = await get_prefix_for_bot(self, message)
            await message.reply(
                lang["main"]["PingForPrefix"][0] + prefix + lang["main"]["PingForPrefix"][1]
            )

        await self.process_commands(message)

    async def on_guild_join(self, guild: Guild):
        """
        Run on guild join.
        """

        self.logger.info(f"Joined {guild.name}")

    async def on_guild_remove(self, guild: Guild):
        """
        Run on guild remove.
        """

        self.logger.info(f"Left {guild.name}")

    async def setup_hook(self):
        """
        Run on startup (yes you can touch this).
        """

        self.quotes = await get_quotes()

        # add ipc routes
        await self.add_cog(Routes(self))

        for cog in COGS:
            await self.add_cog(cog(self))

        await self.load_extension('jishaku')
        self.logger.info("Loaded jishaku")
