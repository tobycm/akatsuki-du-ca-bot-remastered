from time import time
from discord import Interaction
from discord.ext.commands import Context

def redis_log(action : str, status : str): # create redis log function
    with open("log/redis_log.txt", "a") as f: # open redis log file
        f.write(f"Action: {action} with status {status}\n") # write action and status to redis log file
        
def _command_log(author_id : int, guild_id : int, channel_id : int, command : str): # create command log function
    with open("log/commands_log.txt", "a") as f: # open commands log file
        f.write(f"{author_id} used {command} at {int(time())} in {channel_id} in {guild_id}\n") # write command in
        
def command_log(func):
    async def wrapper(itr : Interaction or Context, *args, **kwargs):
        author = itr.user if isinstance(itr, Interaction) else itr.author
        
        result = await func(*args, itr, **kwargs)
        return result
        
    return wrapper
        
def error_log(type : str, error : str): # create error log function
    with open("log/pain.txt", "a") as f: # open error log file
        f.write(f"{type} error:\n{error}") # write error in