from json import load

def get_bot_config(type : str) -> str("value"):
    with open("config/settings.json", "r") as config:
        return load(config)["bot"][type]
    
def get_channel_config(type : str) -> str("value"):
    with open("config/settings.json", "r") as config:
        return load(config)["bot"]["channels"][type]
    
def get_api_key(type : str) -> str("value"):
    with open("config/settings.json", "r") as config:
        return load(config)["api_keys"][type]
    
def get_lavalink_nodes() -> list("node"):
    with open("config/settings.json", "r") as config:
        return load(config)["lavalink_nodes"]
    
def get_redis_config(type : str) -> str("value"):
    with open("config/redis.json", "r") as config:
        return load(config)[type]