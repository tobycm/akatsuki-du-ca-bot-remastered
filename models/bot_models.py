"""
Custom bot model
"""

from time import time
from typing import List
from aioredis import Redis
from discord import Intents
from discord.ext.commands import Bot

from modules.database_utils import return_redis_instance
from modules.load_lang import get_lang


class CustomBot(Bot):
    """
    Custom bot class
    """

    def __init__(self, *args, intents=Intents.all(), **kwargs):
        super().__init__(*args, intents=intents, **kwargs)

    redis_ins: Redis = return_redis_instance()
    lang: dict = get_lang()
    quotes: List[dict]
    quotes_added: float = time()
