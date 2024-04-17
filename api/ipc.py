"""
IPC and routing for bot.
"""

from json import dumps

from discord.ext.commands import Cog
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server

from akatsuki_du_ca import AkatsukiDuCa
from config import config
from modules.log import logger


class Routes(Cog):
    """
    IPC and routing cog for bot
    """

    def __init__(self, bot: AkatsukiDuCa):
        self.bot = bot
        bot.ipc = Server(bot, secret_key = config.bot.secret)

    async def cog_load(self) -> None:
        logger.info("IPC Cog and Server started")
        assert self.bot.ipc
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        logger.info("IPC Cog and Server stopped")
        assert self.bot.ipc
        await self.bot.ipc.stop()
        self.bot.ipc = None

    @Server.route("/user/mutual_servers")
    async def get_user_mutual_server(self, data: ClientPayload) -> str:
        """
        Get user mutual servers
        """

        user = self.bot.get_user(data.user_id)
        if not user:
            return dumps({ "error": "User not found"})
        mutual_servers = user.mutual_guilds
        return dumps({ "servers": mutual_servers })

    @Server.route("/force_join")
    async def user_join_through_oauth(self, _: ClientPayload) -> str:
        """
        An event telling the bot to apologize when user get force-added :troll:
        """

        # doesn't do anything yet

        return "lol"

    @Server.route("/")
    async def alive(self, *_) -> str:
        """
        Check if bot is alive lmao
        """

        return dumps({ "alive": True })
