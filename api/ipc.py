"""
IPC and routing for bot.
"""

from typing import Dict

from discord.ext.commands import Bot, Cog
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload

from modules.vault import get_bot_config

# pylint: disable=protected-access

class Routes(Cog):
    """
    IPC and routing cog for bot
    """
    def __init__(self, bot: Bot):
        self.bot = bot
        bot.ipc = Server(bot, secret_key = get_bot_config("secret"))

    async def cog_load(self) -> None:
        ipc_server: Server = self.bot.ipc
        await ipc_server.start()

    async def cog_unload(self) -> None:
        ipc_server: Server = self.bot.ipc
        await ipc_server.stop()
        self.bot.ipc = None

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> Dict:
        """
        Get user data
        """

        user = self.bot.get_user(data.user_id)
        return user._to_minimal_user_json()
