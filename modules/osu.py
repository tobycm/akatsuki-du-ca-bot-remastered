from aiohttp import ClientSession
from aiosu.models import User as Player
from aiosu.v1 import Client

global client


def load(token: str, session: ClientSession):
    global client
    client = Client(token)
    client._session = session


async def get_player(username: str) -> Player:
    return await client.get_user(username)
