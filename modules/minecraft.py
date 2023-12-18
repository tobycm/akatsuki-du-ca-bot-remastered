"""
Minecraft backend functions for Minecraft cog.
"""

from dataclasses import dataclass
from typing import TypedDict

from aiohttp import ClientSession

UUID = str
Image = str
Thumbnail = str

global session
session: ClientSession | None = None


async def get_minecraft_user(username: str) -> tuple[UUID, Image, Thumbnail]:
    """
    Return a tuple of user's UUID, image and thumbnail.
    """

    global session

    if not session:
        session = ClientSession()

    async with session.get(
        f"https://playerdb.co/api/player/minecraft/{username}"
    ) as response:
        data = await response.json()

        uuid = data["data"]["player"]["id"]
        image = f"https://crafatar.com/renders/body/{uuid}"
        thumbnail = f"https://crafatar.com/avatars/{uuid}"

        return uuid, image, thumbnail


class RawMinecraftServerAPI(TypedDict):
    motd: dict[str, str]
    players: dict[str, int]
    version: str
    icon: str
    online: bool


@dataclass
class Players:
    max: int
    online: int


@dataclass
class MinecraftServer:
    motd: str
    players: Players
    version: str
    icon: str


async def get_minecraft_server(server_ip: str) -> MinecraftServer | None:
    """
    Return a Minecraft server's info as an Embed.
    """

    global session

    if not session:
        session = ClientSession()

    async with session.get(
        url = "https://api.mcsrvstat.us/2/" + server_ip, timeout = 30
    ) as response:
        data: RawMinecraftServerAPI = await response.json()

        if not data["online"]:
            return None

        return MinecraftServer(
            data["motd"]["clean"][0],
            Players(data["players"]["max"], data["players"]["online"]),
            data["version"],
            data["icon"],
        )
