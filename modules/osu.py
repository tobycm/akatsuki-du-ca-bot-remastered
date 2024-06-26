from aiohttp import ClientSession
from aiosu.models import User as Player
from aiosu.v1 import Client

global client
client: Client


async def load(token: str):
    global client
    client = Client(token)


async def get_player(username: str) -> Player:
    return await client.get_user(username)
