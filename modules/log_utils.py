from time import time

def redis_log(action, status):
    with open("log/redis_log.txt", "a") as f:
        f.write(f"Action: {action} with status {status}\n")
        
def command_log(author_id : int, guild_id : int, channel_id : int, command : str):
    with open("log/commands_log.txt", "a") as f:
        f.write(f"{author_id} used {command} at {int(time())} in {channel_id} in {guild_id}\n")
        
def error_log(type : str, error : str):
    with open("log/pain.txt", "a") as f:
        f.write(f"{type} error:\n{error}")