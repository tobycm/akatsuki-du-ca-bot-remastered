from discord import Interaction
from discord.ext.commands import Context
from redis import Redis
from modules.vault import get_redis_config
from modules.database_utils import get_user_lang

async def check_owners(ctx : Context) -> True or False:
   r = Redis(host = get_redis_config("host"), port = get_redis_config("port"), username = get_redis_config("username"), password = get_redis_config("password"), db = get_redis_config("database"))
   result = r.hget("op", ctx.author.id)
   if result is None:
       return False
   return True

def cooldown_check(interaction : Interaction):
    if interaction.guild:
        return interaction.guild.id
    return interaction.user.id


async def return_user_lang(self, id):
    lang_option = await get_user_lang(self.bot.redis_ins, id)
    return self.bot.lang[lang_option]