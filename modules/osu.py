from aiosu.models import User as Player
from aiosu.v1 import Client

global client


def load(token: str):
    global client
    client = Client(token)


async def cleanup():
    await client.close()


async def get_player(username: str) -> Player:
    return await client.get_user(username)
