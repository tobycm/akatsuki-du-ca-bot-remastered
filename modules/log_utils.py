from time import time

def redis_log(action, status): # create redis log function
    with open("log/redis_log.txt", "a") as f: # open redis log file
        f.write(f"Action: {action} with status {status}\n") # write action and status to redis log file
        
def command_log(author_id : int, guild_id : int, channel_id : int, command : str): # create command log function
    with open("log/commands_log.txt", "a") as f: # open commands log file
        f.write(f"{author_id} used {command} at {int(time())} in {channel_id} in {guild_id}\n") # write command in
        
def error_log(type : str, error : str): # create error log function
    with open("log/pain.txt", "a") as f: # open error log file
        f.write(f"{type} error:\n{error}") # write error in