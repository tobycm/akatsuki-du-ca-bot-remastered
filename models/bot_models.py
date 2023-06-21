"""
Custom bot model
"""

import logging
import os
from time import time

from discord import Intents
from discord.ext.commands import Bot
from discord.ext.ipc.server import Server

from modules.database_utils import load_redis
from modules.lang import load_lang


class AkatsukiDuCa(Bot):
    """
    Custom bot class
    """

    def __init__(self, *args, intents=Intents.all(), **kwargs):
        super().__init__(*args, intents=intents, **kwargs)

    load_redis()
    lang: dict = load_lang()
    quotes: list[dict]
    quotes_added: float = time()
    logger: logging.Logger = logging.getLogger("discord")
    ipc: Server

    if not os.path.exists("logs"):
        os.mkdir("logs")

    logging.basicConfig(
        filename="logs/full_bot_log.txt",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )
