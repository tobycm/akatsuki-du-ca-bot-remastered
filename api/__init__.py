from akatsuki_du_ca import AkatsukiDuCa
from api.ipc import Routes


async def setup(bot: AkatsukiDuCa):
    await bot.add_cog(Routes(bot))


async def teardown(bot: AkatsukiDuCa):
    await bot.remove_cog("Routes")
