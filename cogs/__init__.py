from akatsuki_du_ca import AkatsukiDuCa
from cogs.admin import BotAdminCog, PrefixCog
from cogs.fun import FunCog, GIFCog
from cogs.legacy_commands import LegacyCommands
from cogs.music import MusicCog, RadioMusic
from cogs.nsfw import NSFWCog
from cogs.toys import ToysCog
from cogs.utils import MinecraftCog, UtilsCog
from modules.log import logger

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

    await MusicCog.connect_nodes(bot)

    logger.info("Cogs loaded")


async def teardown(bot: AkatsukiDuCa):
    for cog in COGS_LIST:
        await bot.remove_cog(cog.__name__)

    logger.info("Cogs unloaded")
