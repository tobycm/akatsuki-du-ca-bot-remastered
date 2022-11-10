"""
Admin commands for bot in guild.
"""

from logging import Logger
from discord import Interaction
from discord.app_commands import command, checks, MissingPermissions
from discord.ext import commands
from discord.ext.commands import GroupCog, Cog, Context, Bot

from modules.checks_and_utils import check_owners, guild_cooldown_check
from modules.database_utils import delete_prefix, set_prefix

class PrefixCog(GroupCog, name="prefix"):
    """
    Prefix related commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Prefix Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Prefix Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key=guild_cooldown_check)
    @checks.has_permissions(manage_guild=True)
    @command(name="set")
    async def setprefix(self, itr: Interaction, prefix: str):
        """
        Set the bot's prefix
        """

        author = itr.user
        await set_prefix(self.bot.redis_ins, author.guild.id, prefix)
        return await itr.response.send_message(f"Prefix set to `{prefix}`")

    @checks.cooldown(1, 1, key=guild_cooldown_check)
    @checks.has_permissions(manage_guild=True)
    @command(name="reset")
    async def resetprefix(self, itr: Interaction):
        """
        Reset the bot's prefix
        """

        author = itr.user
        await delete_prefix(self.bot.redis_ins, author.guild.id)
        return await itr.response.send_message("Prefix reseted!")


class BotAdminCog(Cog):
    """
    Commands only bot owners can use.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Bot Admin Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Bot Admin Cog unloaded")
        return await super().cog_unload()

    @commands.command(name="resetguildprefix")
    async def resetguildprefix(self, ctx: Context, guild_id: int):
        """
        Reset a guild prefix remotely
        """

        if not await check_owners(self.bot.redis_ins, ctx):
            raise MissingPermissions(["manage_guild"])

        await delete_prefix(self.bot.redis_ins, guild_id)

        return await ctx.send(
            f"Prefix reseted for guild {guild_id}"
        )
