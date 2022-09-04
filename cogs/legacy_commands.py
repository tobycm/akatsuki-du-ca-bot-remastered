"""
These commands are for Toby for trolling only xd
"""

from discord import utils
from discord.ext.commands import command, Context, Cog, MissingRequiredArgument, NotOwner

from models.bot_models import CustomBot

from modules.checks_and_utils import check_owners

class LegacyCommands(Cog):
    """
    Commands Toby use with bots
    """

    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot
        super().__init__()

    @command(name="say")
    async def say(self, ctx: Context, *, value):
        """
        Basically echo
        """

        if not await check_owners(self.bot.redis_ins, ctx):
            raise NotOwner
        if value == "":
            raise MissingRequiredArgument

        await ctx.message.delete()
        return await ctx.send(value)

    @command(name="sayemoji")
    async def sayemoji(self, ctx: Context, emoji_name: str = None, guild_id: int = None):
        """
        Find the emoji and send it
        """

        if emoji_name is None:
            raise MissingRequiredArgument

        if guild_id is None:
            guild_emojis = ctx.guild.emojis
        else:
            guild_emojis = self.bot.get_guild(guild_id).emojis

        emoji = utils.get(guild_emojis, name=emoji_name)
        await ctx.message.delete()
        await ctx.send(emoji if emoji is not None else "lmao")
