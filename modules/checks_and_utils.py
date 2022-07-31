from aioredis import Redis
from discord import Interaction
from discord.ext.commands import Context
from modules.database_utils import get_user_lang

async def check_owners(redis_ins : Redis, ctx : Context or Interaction) -> bool:
   result = await redis_ins.hget("op", ctx.author.id)
   if result is None:
       return False
   return True

def user_cooldown_check(interaction : Interaction):
    return interaction.user.id

def guild_cooldown_check(interaction : Interaction):
    return interaction.guild.id

async def return_user_lang(self, id):
    lang_option = await get_user_lang(self.bot.redis_ins, id)
    return self.bot.lang[lang_option]