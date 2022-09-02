"""
These commands are for Toby for trolling only xd
"""

from discord.ext.commands import command, Context, Cog, MissingRequiredArgument

from models.bot_models import CustomBot

from modules.checks_and_utils import check_owners
from modules.exceptions import NotOwnerLMAO

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
            raise NotOwnerLMAO
        if value == "":
            raise MissingRequiredArgument

        await ctx.message.delete()
        return await ctx.send(value)
