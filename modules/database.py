"""
Database functions module.
"""

import json
from typing import TypedDict

from redis.asyncio import ConnectionPool, Redis

from modules.vault import Redis as RedisConfig

global redis
redis: Redis


def load(config: RedisConfig = RedisConfig()):
    """
    Create and return a Redis instance
    """

    pool: ConnectionPool = ConnectionPool.from_url(
        f"redis://{'' if not config.username and not config.password else f'{config.username}:{config.password}@'}{config.host}:{config.port}/{config.database}",
        max_connections = 5,
    )
    global redis
    redis = Redis(connection_pool = pool)


async def cleanup():
    await redis.close()


# --------------------------------------------- prefix ---------------------------------------------


async def set_prefix(server_id: int, prefix: str) -> None:
    """
    Set a user prefix in database
    """

    await redis.hset("prefix", str(server_id), prefix)


async def delete_prefix(server_id: int) -> None:
    """
    Delete a user prefix in database
    """

    await redis.hdel("prefix", str(server_id))


async def get_prefix(server_id: int) -> str | None:
    """
    Get a user prefix from database
    """

    result = await redis.hget("prefix", str(server_id))
    if result is not None:
        return result.decode()
    return None


# ------------------------------------------- op ----------------------------------------------


class OP(TypedDict):
    reason: str
    adder_id: int


async def set_op(new_op_id: int, reason: str, adder_id: int) -> None:
    """
    Save the new OP Discord ID in database
    """

    await redis.hset(
        "op", str(new_op_id), str({
            "reason": reason,
            "adder_id": adder_id
        })
    )


async def del_op(del_op_id: int) -> None:
    """
    Delete OP Discord ID from database
    """

    await redis.hdel("op", str(del_op_id))


async def get_op(op_id: int) -> OP | None:
    """
    Get all OP data from database
    """

    result = await redis.hget("op", str(op_id))
    if result is not None:
        return json.loads(result.decode())
    return None


# ------------------------------------------ user lang --------------------------------------------


async def set_user_lang(user_id: int, lang_option: str) -> None:
    """
    Set a user language in database
    """

    await redis.hset("user_lang", str(user_id), lang_option)


async def get_user_lang(user_id: int) -> str:
    """
    Get user language from database
    """

    result = await redis.hget("user_lang", str(user_id))
    return result.decode() if result is not None else "en-us"
