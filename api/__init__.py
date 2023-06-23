from api.ipc import Routes
from models.bot_models import AkatsukiDuCa


async def setup(bot: AkatsukiDuCa):
    await bot.add_cog(Routes(bot))


async def teardown(bot: AkatsukiDuCa):
    await bot.remove_cog("Routes")
