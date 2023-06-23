from cogs.admin import BotAdminCog, PrefixCog
from cogs.fun import FunCog, GIFCog
from cogs.legacy_commands import LegacyCommands
from cogs.music import MusicCog, RadioMusic
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import MinecraftCog, UtilsCog
from models.bot_models import AkatsukiDuCa

COGS_LIST = (
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
    LegacyCommands,
)


async def setup(bot: AkatsukiDuCa):
    for cog in COGS_LIST:
        await bot.add_cog(cog(bot))

    bot.logger.info("Cogs loaded")


async def teardown(bot: AkatsukiDuCa):
    for cog in COGS_LIST:
        await bot.remove_cog(cog.__name__)

    bot.logger.info("Cogs unloaded")
