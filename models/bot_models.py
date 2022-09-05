"""
Custom bot model
"""

import logging
from time import time
from typing import List
from aioredis import Redis
from discord import Intents, Message, Guild
from discord.ext.commands import Bot, Context, MissingPermissions, CommandInvokeError

from modules.database_utils import get_prefix, get_user_lang, return_redis_instance
from modules.load_lang import get_lang
from modules.quote_api import get_quotes
from modules.checks_and_utils import get_prefix_for_bot, return_user_lang

from cogs.fun import FunCog, GIFCog
from cogs.music import RadioMusic, MusicCog
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import UtilsCog, MinecraftCog
from cogs.admin import PrefixCog, BotAdminCog
from cogs.legacy_commands import LegacyCommands


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
            lang = self.lang[lang_option]
            prefix = await get_prefix(self.redis_ins, message.guild.id)
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

        await self.load_extension('jishaku')
        self.logger.info("Loaded jishaku")

        await self.add_cog(FunCog(self))
        await self.add_cog(GIFCog(self))
        self.logger.info("-> Fun and GIF Cog added <-")
        await self.add_cog(RadioMusic(self))
        await self.add_cog(MusicCog(self))
        self.logger.info(" -> Radio and Music cog added <-")
        await self.add_cog(NSFWCog(self))
        self.logger.info(" -> NSFW cog added <-")
        await self.add_cog(ToysCog(self))
        self.logger.info(" -> Toys cog added <-")
        await self.add_cog(UtilsCog(self))
        await self.add_cog(MinecraftCog(self))
        self.logger.info(" -> Utils and Minecraft cog added <-")
        await self.add_cog(PrefixCog(self))
        self.logger.info(" -> Prefix cog added <-")
        await self.add_cog(BotAdminCog(self))
        self.logger.info(" -> Bot admin cog added <-")
        await self.add_cog(LegacyCommands(self))
        self.logger.info(" -> Toby sus cog added <-")

    async def on_command_error(self, ctx: Context, exception: Exception) -> None: # pylint: disable=arguments-differ
        """
        Command error handler
        """

        lang = await return_user_lang(self, ctx.author.id)
        prefix = await get_prefix_for_bot(self, ctx.message)

        if isinstance(exception, CommandInvokeError):
            exception = exception.original

        def user_no_perms():
            return lang["MissingGuildPermission"]

        mapping = {
            MissingPermissions: user_no_perms
        }

        await ctx.send(
            content = mapping[exception]()
        )
