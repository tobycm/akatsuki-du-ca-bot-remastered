"""
Vault for the bot secrets and variables.
"""

from dataclasses import dataclass


@dataclass
class ChannelsConfig:
    error: int
    bug: int


@dataclass
class LavalinkNode:
    uri: str = "http://localhost:2333"
    password: str = "youshallnotpass"


@dataclass
class Redis:
    host: str = "localhost"
    port: int = 6379
    username: str = ""
    password: str = ""
    database: int = 0


@dataclass
class HomeGuild:
    id: int
    invite: str


@dataclass
class Bot:
    token: str
    secret: str
    prefix: str
    home_guild: HomeGuild
    channels: ChannelsConfig


@dataclass
class Spotify:
    client_id: str
    client_secret: str


@dataclass
class OsuAPI:
    key: str


@dataclass
class TenorAPI:
    key: str


@dataclass
class API:
    osu: OsuAPI
    tenor: TenorAPI
    spotify: Spotify


@dataclass
class Config:
    bot: Bot
    api: API
    lavalink_nodes: list[LavalinkNode]
    redis: Redis
