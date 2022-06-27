from aioredis import Redis, ConnectionPool

def return_redis_instance(host : str = "localhost", port : int = 6379, username : str = None, password : str = None, db : int = 0):
    pool = ConnectionPool.from_url(
            f"redis://{host}:{port}/{db}",
            max_connections=2,
        )
    return Redis(connection_pool = pool, username = username, password = password)

# -------------------------------------------------- prefix --------------------------------------------------

async def set_prefix(redis_ins : Redis, server_id : int, prefix):
    try:
        await redis_ins.hset("prefix", server_id, prefix)
    except Exception as e:
        return e
    return True

async def delete_prefix(redis_ins : Redis, server_id : int):
    try:
        await redis_ins.hdel("prefix", server_id)
    except Exception as e:
        return e
    return True

async def get_prefix(redis_ins : Redis ,server_id : int):
    result = await redis_ins.hget("prefix", server_id)
    return result.decode()
    
# -------------------------------------------------- op --------------------------------------------------

async def set_op(redis_ins : Redis, new_op_id : int, reason : str, adder_id : int):
    try:
        await redis_ins.hset("op", new_op_id, reason, adder_id)
    except Exception as e:
        return e
    return True

async def del_op(redis_ins : Redis, del_op_id : int):
    try:
        await redis_ins.hdel("op", del_op_id)
    except Exception as e:
        return e
    return True

async def get_op(redis_ins : Redis, op_id : int):
    result = await redis_ins.hget("op", op_id)
    return result.decode()

# -------------------------------------------------- user lang --------------------------------------------------

async def set_user_lang(redis_ins : Redis, user_id : int, lang : str):
    try:
        await redis_ins.hset("user_lang", user_id, lang)
    except Exception as e:
        return e
    return True

async def get_user_lang(redis_ins : Redis, user_id : int):
    result = await redis_ins.hget("user_lang", user_id)
    return result.decode()