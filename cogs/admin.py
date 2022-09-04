"""
Admin commands for bot in guild.
"""

from discord import Interaction
from discord.app_commands import command, checks, MissingPermissions
from discord.ext import commands
from discord.ext.commands import GroupCog, Cog, Context, Bot

from modules.checks_and_utils import check_owners, guild_cooldown_check
from modules.database_utils import delete_prefix, set_prefix
from modules.vault import get_channel_config


class PrefixCog(GroupCog, name="prefix"):
    """
    Prefix related commands.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()

    @checks.cooldown(1, 1, key=guild_cooldown_check)
    @checks.has_permissions(manage_guild=True)
    @command(name="set")
    async def setprefix(self, itr: Interaction, prefix: str):
        """
        Set the bot's prefix
        """

        author = itr.user
        result = await set_prefix(self.bot.redis_ins, author.guild.id, prefix)

        if result:
            return await itr.response.send_message(f"Prefix set to `{prefix}`")

        await itr.response.send_message("Fail to set prefix")

        error_channel = self.bot.get_channel(get_channel_config("error"))
        return await error_channel.send(
            f"{author} tried to set prefix to `{prefix}` but failed. Error: {result}"
        )

    @checks.cooldown(1, 1, key=guild_cooldown_check)
    @checks.has_permissions(manage_guild=True)
    @command(name="reset")
    async def resetprefix(self, itr: Interaction):
        """
        Reset the bot's prefix
        """

        author = itr.user
        result = await delete_prefix(self.bot.redis_ins, author.guild.id)

        if result:
            return await itr.response.send_message("Prefix reseted!")

        await itr.response.send_message("Fail to set prefix")

        error_channel = self.bot.get_channel(get_channel_config("error"))
        return await error_channel.send(
            f"{author} tried to reset prefix but failed. Error: {result}"
        )


class BotAdminCog(Cog):
    """
    Commands only bot owners can use.
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="resetguildprefix")
    async def resetguildprefix(self, ctx: Context, guild_id: int):
        """
        Reset a guild prefix remotely
        """

        if not await check_owners(self.bot.redis_ins, ctx):
            raise MissingPermissions(["manage_guild"])

        result = await delete_prefix(self.bot.redis_ins, guild_id)

        return await ctx.send(
            f"Prefix reseted for guild {guild_id}" if result else f"Fail to reset prefix. Error: {result}"
        )
