"""
Custom bot model
"""

import logging
import os
from time import time

from aiohttp import ClientSession
from discord import Intents
from discord.ext.commands import Bot
from discord.ext.ipc.server import Server

from modules.vault import Config


class AkatsukiDuCa(Bot):
    """
    Custom bot class
    """

    def __init__(self, *args, intents = Intents.all(), **kwargs):
        super().__init__(*args, intents = intents, **kwargs)

    logger: logging.Logger = logging.getLogger("discord")
    ipc: Server | None = None
    config: Config
    session = ClientSession()

    if not os.path.exists("logs"):
        os.mkdir("logs")

    if os.path.exists("logs/full_bot_log.txt"):
        os.rename(
            "logs/full_bot_log.txt", f"logs/full_bot_log_{int(time())}.txt"
        )

    logging.basicConfig(
        filename = "logs/full_bot_log.txt",
        format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt = "%H:%M:%S",
        level = logging.INFO,
    )
