"""
Minecraft backend functions for Minecraft cog.
"""

from discord import Embed
from aiohttp import ClientSession


async def get_minecraft_user_embed(username: str) -> tuple(["uuid", "image", "thumbnail"]):
    """
    Return a tuple of user's UUID, image and thumbnail.
    """

    async with ClientSession() as session:
        async with session.get("https://playerdb.co/api/player/minecraft/" + username) as response:
            data = await response.json()

            uuid = data["data"]["player"]["id"]
            image = f"https://crafatar.com/renders/body/{uuid}"
            thumbnail = f"https://crafatar.com/avatars/{uuid}"

            return (uuid, image, thumbnail)


async def get_minecraft_server_info(server_ip: str) -> Embed:
    """
    Return a Minecraft server's info as an Embed.
    """

    async with ClientSession() as session:
        async with session.get("https://api.mcsrvstat.us/2/" + server_ip) as response:
            data = await response.json()

            if data["online"] is False:
                return False

            return {
                "motd": data["motd"]["clean"],
                "players": [data["players"]["online"], data["players"]["max"]],
                "version": data["version"],
                "icon": data["icon"].replace('\\', '')
            }
