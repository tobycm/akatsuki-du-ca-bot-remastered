"""
Admin commands for bot in guild.
"""

from logging import Logger

from discord import Interaction
from discord.app_commands import MissingPermissions, checks, command
from discord.ext import commands
from discord.ext.commands import Cog, Context, GroupCog

from akatsuki_du_ca import AkatsukiDuCa
from modules.database import delete_prefix, set_prefix
from modules.misc import check_owners, guild_cooldown_check


class PrefixCog(GroupCog, name="prefix"):
    """
    Prefix related commands.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
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
    async def setprefix(self, interaction: Interaction, prefix: str):
        """
        Set the bot's prefix
        """

        assert interaction.guild
        await set_prefix(interaction.guild.id, prefix)
        return await interaction.response.send_message(f"Prefix set to `{prefix}`")

    @checks.cooldown(1, 1, key=guild_cooldown_check)
    @checks.has_permissions(manage_guild=True)
    @command(name="reset")
    async def resetprefix(self, interaction: Interaction):
        """
        Reset the bot's prefix
        """

        assert interaction.guild
        await delete_prefix(interaction.guild.id)
        return await interaction.response.send_message("Prefix reseted!")


class BotAdminCog(Cog):
    """
    Commands only bot owners can use.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
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
        Reset a guild prefix
        """

        if not await check_owners(ctx):
            raise MissingPermissions(["manage_guild"])

        await delete_prefix(guild_id)

        return await ctx.send(f"Prefix reseted for guild {guild_id}")
