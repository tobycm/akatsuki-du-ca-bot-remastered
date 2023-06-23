from aiosu.models import User
from aiosu.v1 import Client

global client


def load(token: str):
    global client
    client = Client(token)


async def cleanup():
    await client.close()


async def get_user(username: str) -> User:
    return await client.get_user(username)
