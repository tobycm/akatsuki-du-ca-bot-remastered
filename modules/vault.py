from json import load
from typing import List

def get_bot_config(val : str) -> str:
    with open("config/settings.json", "r") as config:
        return load(config)["bot"][val]
    
def get_channel_config(type : str) -> str:
    with open("config/settings.json", "r") as config:
        return load(config)["bot"]["channels"][type]
    
def get_api_key(type : str) -> str:
    with open("config/settings.json", "r") as config:
        return load(config)["api_keys"][type]
    
def get_lavalink_nodes() -> List[dict]:
    with open("config/settings.json", "r") as config:
        return load(config)["lavalink_nodes"]
    
def get_redis_config(type : str) -> str:
    with open("config/redis.json", "r") as config:
        return load(config)[type]