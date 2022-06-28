from discord.ext.commands import Context
from redis import Redis
from modules.vault import get_redis_config

async def check_owners(ctx : Context):
   r = Redis(host = get_redis_config("host"), port = get_redis_config("port"), username = get_redis_config("username"), password = get_redis_config("password"), db = get_redis_config("database"))
   result = r.hget("op", ctx.author.id)
   if result is None:
       return False
   return True