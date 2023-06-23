"""
Vault for the bot secrets and variables.
"""

import json
from dataclasses import dataclass


@dataclass
class ChannelsConfig:
    error: int
    bug: int


@dataclass
class ApiKeys:
    osu: str
    tenor: str


@dataclass
class BotLavalinkConfig:
    uri: str
    password: str


@dataclass
class RedisConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class BotConfig:
    token: str
    secret: str
    prefix: str
    home_guild_id: int
    home_guild_invite: str
    channels: ChannelsConfig
    api_keys: ApiKeys
    lavalink_nodes: list[BotLavalinkConfig]
    redis: RedisConfig


def load() -> BotConfig:
    with open("config.json", "r", encoding="utf8") as config:
        return BotConfig(**json.load(config)["bot"])
