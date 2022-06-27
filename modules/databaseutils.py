from redis import Redis

def return_redis_instance(host : str = "localhost", port : int = 6379, password : str = None, db : int = 0):
    return Redis(host = host, port = port, password = password, db = db)

# -------------------------------------------------- prefix --------------------------------------------------

def set_prefix(redis_ins : Redis, server_id : int, prefix):
    try:
        redis_ins.hset("prefix", server_id, prefix)
    except Exception as e:
        return e
    return True

def delete_prefix(redis_ins : Redis, server_id : int):
    try:
        redis_ins.hdel("prefix", server_id)
    except Exception as e:
        return e
    return True

def get_prefix(redis_ins : Redis ,server_id : int):
    return redis_ins.hget("prefix", server_id).decode()
    
# -------------------------------------------------- op --------------------------------------------------

def set_op(redis_ins : Redis, new_op_id : int, reason : str, adder_id : int):
    try:
        redis_ins.hset("op", new_op_id, reason, adder_id)
    except Exception as e:
        return e
    return True

def set_op(redis_ins : Redis, del_op_id : int):
    try:
        redis_ins.hdel("op", del_op_id)
    except Exception as e:
        return e
    return True

# -------------------------------------------------- user lang --------------------------------------------------

def set_user_lang(redis_ins : Redis, user_id : int, lang : str):
    try:
        redis_ins.hset("user_lang", user_id, lang)
    except Exception as e:
        return e
    return True

def get_user_lang(redis_ins : Redis, user_id : int):
    return redis_ins.hget("user_lang", user_id).decode()