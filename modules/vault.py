"""
Vault for the bot secrets and variables.
"""

from json import load
from typing import List


def get_bot_config(value: str) -> str:
    """
    Return a bot config value.
    """

    with open("config/settings.json", "r", encoding = "utf8") as config:
        return load(config)["bot"][value]


def get_channel_config(value: str) -> str:
    """
    Return a channel ID with the corresponding type.
    """

    with open("config/settings.json", "r", encoding = "utf8") as config:
        return load(config)["bot"]["channels"][value]


def get_api_key(service: str) -> str:
    """
    Get an API key from the config.
    """

    with open("config/settings.json", "r", encoding = "utf8") as config:
        return load(config)["api_keys"][service]


def get_lavalink_nodes() -> List[dict]:
    """
    Return a list of lavalink nodes.
    """

    with open("config/settings.json", "r", encoding = "utf8") as config:
        return load(config)["lavalink_nodes"]


def get_redis_config(value: str) -> str:
    """
    Return a Redis database config value.
    """

    with open("config/redis.json", "r", encoding = "utf8") as config:
        return load(config)[value]
