from json import load

def get_bot_config(type) -> str("value"):
    with open("config/settings.json", "r") as config:
        return load(config)[type]
    
def get_redis_config(type) -> str("value"):
    with open("config/redis.json", "r") as config:
        return load(config)[type]