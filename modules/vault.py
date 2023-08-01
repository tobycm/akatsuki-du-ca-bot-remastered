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
    uri: str = "http://localhost:2333"
    password: str = "youshallnotpass"


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    username: str = ""
    password: str = ""
    database: str = "0"


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
    with open("config.json", "r", encoding="utf8") as file:
        config = json.load(file)
        return BotConfig(
            token=config["bot"]["token"],
            secret=config["bot"]["secret"],
            prefix=config["bot"]["prefix"],
            home_guild_id=config["bot"]["home_guild_id"],
            home_guild_invite=config["bot"]["home_guild_invite"],
            channels=ChannelsConfig(
                error=config["bot"]["channels"]["error"],
                bug=config["bot"]["channels"]["bug"],
            ),
            api_keys=ApiKeys(
                osu=config["api_keys"]["osu"],
                tenor=config["api_keys"]["tenor"],
            ),
            lavalink_nodes=[
                BotLavalinkConfig(
                    uri=config["lavalink_nodes"][0]["uri"],
                    password=config["lavalink_nodes"][0]["password"],
                )
            ],
            redis=RedisConfig(
                host=config["redis"]["host"],
                port=config["redis"]["port"],
                username=config["redis"]["username"],
                password=config["redis"]["password"],
                database=config["redis"]["database"],
            ),
        )
