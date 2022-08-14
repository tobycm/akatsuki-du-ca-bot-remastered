"""
Log utilities
"""

from time import time
from discord import Interaction
from discord.ext.commands import Context


def redis_log(action: str, status: str):  # create redis log function
    """
    Log redis actions
    """

    with open("log/redis_log.txt", "a", encoding="utf8") as file:  # open redis log file
        # write action and status to redis log file
        file.write(f"Action: {action} with status {status}\n")


# create command log function
def _command_log(author_id: int, guild_id: int, channel_id: int, command: str):
    with open("log/commands_log.txt", "a", encoding="utf8") as file:  # open commands log file
        # write command in
        file.write(
            f"{author_id} used {command} at {int(time())} in {channel_id} in {guild_id}\n")


def command_log(func):
    """
    Log commands
    """

    async def wrapper(itr: Interaction or Context, *args, **kwargs):
        # author = itr.user if isinstance(itr, Interaction) else itr.author

        result = await func(*args, itr, **kwargs)
        return result

    return wrapper


def error_log(error_object: str, error: str):  # create error log function
    """
    Log errors
    """

    with open("log/pain.txt", "a", encoding="utf8") as file:  # open error log file
        file.write(f"{error_object} error:\n{error}")  # write error in
