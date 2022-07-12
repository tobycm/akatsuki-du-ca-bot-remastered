from discord import Embed, app_commands, Interaction
from discord.ext.commands import Cog

from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.embed_process import rich_embeds
from modules.log_utils import command_log
from modules.osu_api import get_osu_user_info

class UtilsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 0.25, key = user_cooldown_check)
    @app_commands.command(name = "osu")
    async def osu(self, interaction : Interaction, user : str):
        """
        Get osu! stats for a user
        """

        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        lang = await return_user_lang(self, author.id)
        
        osu_user_data = await get_osu_user_info(user)
        if osu_user_data is None:
            await interaction.response.send_message(lang["utils"]["osuUserNotFound"])
            return
        
        temp_description = lang["utils"]["osuStatsDescription"]
        i = 0
        
        for k, v in osu_user_data.items():
            temp_description[i] += str(v)
            i += 1

        return await interaction.response.send_message(embed = rich_embeds(
            Embed(title = lang["utils"]["osuStatsTitle"] % (user),
                  description = "\n".join(temp_description),
                 ).set_thumbnail(url = f"http://s.ppy.sh/a/{osu_user_data['user_id']}")
                  .set_author(name = "osu! user data", icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png"),
            author,
            lang["main"]
        ))