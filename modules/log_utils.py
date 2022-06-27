from discord.ext.commands import Context
from time import time

def redis_log(action, status):
    with open("log/redis_log.txt", "a") as f:
        f.write(f"Action: {action} with status {status}\n")
        
def command_log(ctx : Context, command : str):
    with open("log/commands_log.txt", "a") as f:
        f.write(f"{ctx.author.id} used {command} at {int(time())} in {ctx.channel.id} in {ctx.guild.id}\n")
        
def error_log(type : str, error : str):
    with open("log/pain.txt", "a") as f:
        f.write(f"{type} error:\n{error}")