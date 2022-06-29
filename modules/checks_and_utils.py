from discord import Interaction
from discord.ext.commands import Context
from modules.database_utils import get_user_lang

async def check_owners(self, ctx : Context) -> True or False:
   result = self.bot.redis_ins.hget("op", ctx.author.id)
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