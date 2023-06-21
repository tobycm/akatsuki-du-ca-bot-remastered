"""
Database functions module.
"""

import json
from typing import Optional

from aioredis import ConnectionPool, Redis

global redis


def load_redis(
    host: str = "localhost",
    port: int = 6379,
    username: str = None,
    password: str = None,
    database: int = 0,
) -> Redis:
    """
    Create and return a Redis instance
    """

    pool = ConnectionPool.from_url(
        f"redis://{host}:{port}/{database}",
        max_connections=2,
    )
    global redis
    redis = Redis(connection_pool=pool, username=username, password=password)


# --------------------------------------------- prefix ---------------------------------------------


async def set_prefix(server_id: int, prefix: str) -> None:
    """
    Set a user prefix in database
    """

    await redis.hset("prefix", server_id, prefix)


async def delete_prefix(server_id: int) -> None:
    """
    Delete a user prefix in database
    """

    await redis.hdel("prefix", server_id)


async def get_prefix(server_id: int) -> Optional[str]:
    """
    Get a user prefix from database
    """

    result = await redis.hget("prefix", server_id)
    if result is not None:
        return result.decode()


# ------------------------------------------- op ----------------------------------------------


async def set_op(new_op_id: int, reason: str, adder_id: int) -> None:
    """
    Save the new OP Discord ID in database
    """

    await redis.hset("op", new_op_id, str({"reason": reason, "adder_id": adder_id}))


async def del_op(del_op_id: int) -> None:
    """
    Delete OP Discord ID from database
    """

    await redis.hdel("op", del_op_id)


async def get_op(op_id: int) -> Optional[dict]:
    """
    Get all OP data from database
    """

    result = await redis.hget("op", op_id)
    if result is not None:
        return json.loads(result.decode())


# ------------------------------------------ user lang --------------------------------------------


async def set_user_lang(user_id: int, lang: str) -> None:
    """
    Set a user language in database
    """

    await redis.hset("user_lang", user_id, lang)


async def get_user_lang(user_id: int) -> str:
    """
    Get user language from database
    """

    result = await redis.hget("user_lang", user_id)
    return result.decode() if result is not None else "en-us"
