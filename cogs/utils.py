"""
Utilities for the bot.
"""

from logging import Logger
from typing import Optional

from discord import AllowedMentions, Embed, Interaction, Member
from discord.app_commands import command, checks
from discord.ext.commands import Cog, GroupCog, Bot
from discord.ui import View

from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.embed_process import rich_embeds
from modules.minecraft_utils import get_minecraft_server_info, get_minecraft_user_embed
from modules.osu_api import get_osu_user_info
from modules.vault import get_channel_config
from modules.load_lang import lang_list

from models.utils_models import ChangeLang


class UtilsCog(Cog):
    """
    Utilities commands for user.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Utilities Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Utilities Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="osu")
    async def osu(self, itr: Interaction, user: str):
        """
        Get osu! stats for a user
        """

        author = itr.user

        lang = await return_user_lang(self.bot, author.id)

        osu_user_data = await get_osu_user_info(user)
        if osu_user_data is None:
            await itr.response.send_message(lang["utils"]["osuUserNotFound"])
            return

        lang_desc = lang["utils"]["osuStatsDescription"]
        i = 0
        desc = []

        for key, value in osu_user_data.items():
            if key == "country":
                value = f":flag_{value}:"
            desc.append(lang_desc[i] + str(value))
            i += 1

        embed = rich_embeds(
            Embed(title=lang["utils"]["osuStatsTitle"] % (user,),
                  description="\n".join(desc),
                  )
            .set_thumbnail(
                url=f"http://s.ppy.sh/a/{osu_user_data['user_id']}"
            )
            .set_author(
                name="osu! user data",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png"
            ),
            author,
            lang["main"]
        )

        return await itr.response.send_message(embed=embed)

    @checks.cooldown(1, 2.5, key=user_cooldown_check)
    @command(name="bugreport")
    async def bugreport(self, itr: Interaction, bug_description: str):
        """
        Report a bug. Use wisely
        """

        author = itr.user

        bug_channel = self.bot.get_channel(get_channel_config("bug"))

        await itr.response.send_message(
            "Thank you for your bug report. It will be reviewed shortly."
        )

        await bug_channel.send(
            f"{author} báo lỗi: {bug_description}",
            allowed_mentions=AllowedMentions(
                users=False,
                roles=False,
                everyone=False
            )
        )
        return await bug_channel.send(f"User ID: {author.id} | Guild ID: {author.guild.id}")

    @checks.cooldown(1, 30, key=user_cooldown_check)
    @command(name="change_language")
    async def change_language(self, itr: Interaction):
        """
        Start an interactive language change session. hehe
        """

        select_menu = ChangeLang(
            bot=self.bot,
            author=itr.user
        )

        for option in lang_list:
            select_menu.add_option(label=option, value=option)

        view = View(timeout=30).add_item(select_menu)

        await itr.response.send_message(
            content="Please select a language",
            view=view,
            ephemeral=True
        )

        if await view.wait():
            select_menu: ChangeLang = view.children[0]
            select_menu.disabled = True
            return await itr.edit_original_response(view=view)

    @checks.cooldown(1, 2, key=user_cooldown_check)
    @command(name="ping")
    async def ping_bot(self, itr: Interaction):
        """
        Check and send bot ping/latency
        """

        await itr.response.send_message(
            content=f"\U0001f3d3 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="server_info")
    async def server_info(self, itr: Interaction):
        """
        Send server info
        """
        guild = itr.guild
        lang = await return_user_lang(self.bot, itr.user.id)
        embed = Embed(title="Server Info", description="")

        embed.add_field(name="Server Name", value=guild.name)
        embed.add_field(name="Server ID", value=guild.id)
        embed.add_field(name="Server Owner", value=guild.owner)
        embed.add_field(name="Server Age", value=f"<t:{int(guild.created_at.timestamp())}:D>")
        embed.add_field(name="Server Member Count", value=guild.member_count)
        embed.add_field(name="Server Verification Level", value=guild.verification_level)
        embed.set_thumbnail(url=guild.icon.url)

        await itr.response.send_message(
            embed=rich_embeds(
                embed=embed,
                author=itr.user,
                lang=lang["main"]
            )
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="user_info")
    async def user_info(self, itr: Interaction, user: Optional[Member] = None):
        """
        Send user info
        """

        lang = await return_user_lang(self.bot, itr.user.id)

        if user is None:
            user: Member = itr.user

        embed = Embed(title="User Info", description="")

        embed.add_field(name="User Name", value=user.name)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="User Status", value=user.status)
        embed.add_field(name="User Joined Date", value=f"<t:{int(user.joined_at.timestamp())}:D>")
        embed.add_field(name="User Creation Date", value=f"<t:{int(user.created_at.timestamp())}:D>")
        embed.add_field(
            name="User Roles",
            value=", ".join([
                role.name for role in user.roles if not role.is_default()
            ]) if len(user.roles) != 1 else "No Roles",
            inline=False)
        embed.set_thumbnail(url=user.avatar.url)

        await itr.response.send_message(
            embed=rich_embeds(
                embed=embed,
                author=user,
                lang=lang["main"]
            )
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="avatar")
    async def avatar(self, itr: Interaction, user: Optional[Member] = None):
        """
        Get a user avatar
        """

        lang = await return_user_lang(self.bot, itr.user.id)

        if user is None:
            user: Member = itr.user

        embed = rich_embeds(
            embed = Embed(
                title = "Avatar"
            ),
            author = itr.user,
            lang=lang["main"]
        )

        embed.set_image(url = user.avatar.url)
        await itr.response.send_message(embed=embed)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="server_icon")
    async def server_icon(self, itr: Interaction):
        """
        Get a user avatar
        """

        lang = await return_user_lang(self.bot, itr.user.id)

        embed = rich_embeds(
            embed = Embed(
                title = "Server Icon",
            ),
            author = itr.user,
            lang=lang["main"]
        )

        embed.set_image(url = itr.guild.icon.url)
        await itr.response.send_message(embed=embed)

class MinecraftCog(GroupCog, name="minecraft"):
    """
    Minecraft related commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger: Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Minecraft Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Minecraft Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="java_user")
    async def java_user(self, itr: Interaction, user: str):
        """
        Find info (mostly skin) about a Minecraft Java player
        """

        author = itr.user

        lang = await return_user_lang(self.bot, author.id)

        uuid, image, thumbnail = await get_minecraft_user_embed(user)
        embed = rich_embeds(
            Embed(
                title=lang["utils"]["MinecraftAccount"][0] + user,
                description=f"{lang['utils']['MinecraftAccount'][1]}{user}\nUUID: {uuid}"
            ).set_image(
                url=image
            ).set_thumbnail(
                url=thumbnail
            ),
            author,
            lang["main"])

        return await itr.response.send_message(embed=embed)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="java_server")
    async def java_server(self, itr: Interaction, server_ip: str):
        """
        Find info about a Minecraft Java server
        """

        author = itr.user

        lang = await return_user_lang(self.bot, author.id)
        mc_server_lang = lang['utils']['MinecraftServer']

        data = await get_minecraft_server_info(server_ip)

        if data is False:
            return await itr.response.send_message(lang["utils"]["MinecraftServer"]["NotFound"])

        motd = "```" + '\n'.join([i for i in data['motd']]) + "```"
        server_info = mc_server_lang['ServerIp'] + server_ip
        version = mc_server_lang['version'] + data['version']
        players = mc_server_lang['players'] + data['players'][0] + "/" + data['players'][1]

        embed = rich_embeds(
            Embed(
                title=f"{server_ip} {mc_server_lang['online' if data['online'] else 'offline']}",
                description= "\n".join([motd, server_info, version, players])
            ),
            author,
            lang["main"]
        )

        return await itr.response.send_message(embed=embed)
