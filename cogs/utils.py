from discord import AllowedMentions, Embed, app_commands, Interaction
from discord.ext.commands import Cog, GroupCog

from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.embed_process import rich_embeds
from modules.log_utils import command_log
from modules.minecraft_utils import get_minecraft_server_info, get_minecraft_user_embed
from modules.osu_api import get_osu_user_info

class UtilsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
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
        
        lang_desc = lang["utils"]["osuStatsDescription"]
        i = 0
        desc = []
        
        for k, v in osu_user_data.items():
            if k == "country":
                v = f":flag_{v}:"
            desc.append(lang_desc[i] + str(v))
            i += 1
            
        embed = rich_embeds(
            Embed(title = lang["utils"]["osuStatsTitle"] % (user,),
                  description = "\n".join(desc),
                 ).set_thumbnail(url = f"http://s.ppy.sh/a/{osu_user_data['user_id']}")
                  .set_author(name = "osu! user data", icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png"),
            author,
            lang["main"]
        )
        
        return await interaction.response.send_message(embed = embed)
            
    @app_commands.checks.cooldown(1, 2.5, key = user_cooldown_check)
    @app_commands.command(name = "bugreport")
    async def bugreport(self, interaction : Interaction, bug_description : str):
        """
        Report a bug. Use wisely
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        bug_channel = self.bot.get_channel(912563176447561796)
        
        await interaction.response.send_message("Thank you for your bug report. It will be reviewed shortly.")
        
        await bug_channel.send(
            f"{author} báo lỗi: {bug_description}",
            allowed_mentions=AllowedMentions(
                users=False,
                roles=False,
                everyone=False
                )
            )
        return await bug_channel.send(f"User ID: {author.id} | Guild ID: {author.guild.id}")
    
class MinecraftCog(GroupCog, name = "minecraft"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "java_user")
    async def java_user(self, interaction : Interaction, user : str):
        """
        Find info (mostly skin) about a Minecraft Java player
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        lang = await return_user_lang(self, author.id)
        
        uuid, image, thumbnail = await get_minecraft_user_embed(user)
        embed = rich_embeds(
                Embed(
                    title = lang["utils"]["MinecraftAccount"][0] + user,
                    description = f"{lang['utils']['MinecraftAccount'][1]}{user}\nUUID: {uuid}"
                ).set_image(
                    url = image
                ).set_thumbnail(
                    url = thumbnail
                ),
                author,
                lang["main"])
        
        return await interaction.response.send_message(embed = embed)
    
    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "java_server")
    async def java_server(self, interaction : Interaction, server_ip : str):
        """
        Find info about a Minecraft Java server
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        lang = await return_user_lang(self, author.id)
        
        data = await get_minecraft_server_info(server_ip)
        
        if data is False:
            return await interaction.response.send_message(lang["utils"]["MinecraftServer"]["NotFound"])
        
        motd = "```" + '\n'.join([i for i in data['motd']]) + "```"
        server_info = lang['utils']['MinecraftServer']['server_info'] + server_ip
        version = lang['utils']['MinecraftServer']['version'] + data['version']
        players = f"{lang['utils']['MinecraftServer']['players']}{data['players'][0]}/{data['players'][1]}"
        
        embed = rich_embeds(
                    Embed(
                        title = f"{server_ip} {lang['utils']['MinecraftServer']['online']}",
                        description = f"{motd.lstrip()}\n{server_info}\n{version}\n{players}"
                    ),
                    author,
                    lang["main"]
                )
        
        return await interaction.response.send_message(embed = embed)
    
    