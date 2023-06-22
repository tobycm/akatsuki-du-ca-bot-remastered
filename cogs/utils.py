"""
Utilities for the bot.
"""

from logging import Logger
from typing import Optional, Union

from discord import AllowedMentions, Embed, Interaction, Member, TextChannel, User
from discord.app_commands import checks, command
from discord.ext.commands import Bot, Cog, GroupCog
from discord.ui import View

from models.bot_models import AkatsukiDuCa
from models.utils_models import ChangeLang
from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.embed_process import rich_embeds
from modules.lang import get_lang, get_lang_by_address, lang_list
from modules.minecraft_utils import get_minecraft_server_info, get_minecraft_user_embed
from modules.osu_api import get_osu_user_info
from modules.vault import get_channel_config


class UtilsCog(Cog):
    """
    Utilities commands for user.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
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
    async def osu(self, interaction: Interaction, user: str):
        """
        Get osu! stats for a user
        """

        author = interaction.user

        lang = await get_lang(author.id)

        osu_user_data = await get_osu_user_info(user)
        if osu_user_data is None:
            await interaction.response.send_message(
                get_lang_by_address("utils.osuUserNotFound", lang)
            )
            return

        lang_desc = get_lang_by_address("utils.osuStatsDescription", lang)
        i = 0
        desc = []

        for key, value in osu_user_data.items():
            if key == "country":
                value = f":flag_{value}:"
            desc.append(lang_desc[i] + str(value))
            i += 1

        embed = rich_embeds(
            Embed(
                title=get_lang_by_address("utils.osuStatsTitle", lang) % (user,),  # type: ignore
                description="\n".join(desc),
            )
            .set_thumbnail(url=f"http://s.ppy.sh/a/{osu_user_data['user_id']}")
            .set_author(
                name="osu! user data",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png",
            ),
            author,
            lang,
        )

        return await interaction.response.send_message(embed=embed)

    @checks.cooldown(1, 2.5, key=user_cooldown_check)
    @command(name="bugreport")
    async def bugreport(self, interaction: Interaction, bug_description: str):
        """
        Report a bug. Use wisely
        """

        author = interaction.user

        bug_channel = self.bot.get_channel(get_channel_config("bug"))

        await interaction.response.send_message(
            "Thank you for your bug report. It will be reviewed shortly."
        )

        assert isinstance(bug_channel, TextChannel)
        assert isinstance(author, Member)

        await bug_channel.send(
            f"{author} báo lỗi: {bug_description}",
            allowed_mentions=AllowedMentions(users=False, roles=False, everyone=False),
        )
        return await bug_channel.send(
            f"User ID: {author.id} | Guild ID: {author.guild.id}"
        )

    @checks.cooldown(1, 30, key=user_cooldown_check)
    @command(name="change_language")
    async def change_language(self, interaction: Interaction):
        """
        Start an interactive language change session. hehe
        """

        select_menu = ChangeLang(interaction.user)

        for option in lang_list:
            select_menu.add_option(label=option, value=option)

        view = View(timeout=30).add_item(select_menu)

        await interaction.response.send_message(
            content="Please select a language", view=view, ephemeral=True
        )

        if await view.wait():
            assert isinstance(view.children[0], ChangeLang)
            view.children[0].disabled = True
            return await interaction.edit_original_response(view=view)

    @checks.cooldown(1, 2, key=user_cooldown_check)
    @command(name="ping")
    async def ping_bot(self, interaction: Interaction):
        """
        Check and send bot ping/latency
        """

        await interaction.response.send_message(
            content=f"\U0001f3d3 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="server_info")
    async def server_info(self, interaction: Interaction):
        """
        Send server info
        """

        assert interaction.guild
        guild = interaction.guild
        embed = Embed(title="Server Info", description="")

        embed.add_field(name="Server Name", value=guild.name)
        embed.add_field(name="Server ID", value=guild.id)
        embed.add_field(name="Server Owner", value=guild.owner)
        embed.add_field(
            name="Server Age", value=f"<t:{int(guild.created_at.timestamp())}:D>"
        )
        embed.add_field(name="Server Member Count", value=guild.member_count)
        embed.add_field(
            name="Server Verification Level", value=guild.verification_level
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        await interaction.response.send_message(
            embed=rich_embeds(
                embed, interaction.user, await get_lang(interaction.user.id)
            )
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="user_info")
    async def user_info(self, interaction: Interaction, user: Optional[Member]): # type: ignore
        """
        Send user info
        """

        if not user:
            assert isinstance(interaction.user, Member)
            user: Member = interaction.user
        assert user.joined_at

        embed = Embed(title="User Info", description="")

        embed.add_field(name="User Name", value=user.name)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="User Status", value=user.status)
        embed.add_field(
            name="User Joined Date", value=f"<t:{int(user.joined_at.timestamp())}:D>"
        )
        embed.add_field(
            name="User Creation Date", value=f"<t:{int(user.created_at.timestamp())}:D>"
        )
        embed.add_field(
            name="User Roles",
            value=", ".join(
                [role.mention for role in user.roles if not role.is_default()]
            )
            if len(user.roles) != 1
            else "No Roles",
            inline=False,
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)

        await interaction.response.send_message(
            embed=rich_embeds(embed, user, await get_lang(interaction.user.id)),
            allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False),
        )

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="avatar")
    async def avatar(self, interaction: Interaction, user: Optional[Member] = None): # type: ignore
        """
        Get a user avatar
        """

        if not user:
            assert isinstance(interaction.user, Member)
            user: Member = interaction.user

        embed = rich_embeds(
            Embed(title="Avatar"), interaction.user, await get_lang(interaction.user.id)
        )

        embed.set_image(url=user.avatar.url if user.avatar else None)
        await interaction.response.send_message(embed=embed)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="server_icon")
    async def server_icon(self, interaction: Interaction):
        """
        Get a user avatar
        """

        assert interaction.guild

        embed = rich_embeds(
            Embed(
                title="Server Icon",
            ),
            interaction.user,
            await get_lang(interaction.user.id),
        )

        embed.set_image(
            url=interaction.guild.icon.url if interaction.guild.icon else None
        )
        await interaction.response.send_message(embed=embed)


class MinecraftCog(GroupCog, name="minecraft"):
    """
    Minecraft related commands.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
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
    async def java_user(self, interaction: Interaction, user: str):
        """
        Find info (mostly skin) about a Minecraft Java player
        """

        author = interaction.user

        lang = await get_lang(author.id)

        uuid, image, thumbnail = await get_minecraft_user_embed(user)
        embed = rich_embeds(
            Embed(
                title=get_lang_by_address("utils.MinecraftAccount", lang)[0] + user,
                description=get_lang_by_address("utils.MinecraftAccount", lang)[1]
                + user
                + f"\nUUID: {uuid}",
            )
            .set_image(url=image)
            .set_thumbnail(url=thumbnail),
            author,
            lang,
        )

        return await interaction.response.send_message(embed=embed)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="java_server")
    async def java_server(self, interaction: Interaction, server_ip: str):
        """
        Find info about a Minecraft Java server
        """

        author = interaction.user

        lang = await get_lang(author.id)
        mc_server_lang = get_lang_by_address("utils.MinecraftServer", lang)

        data = await get_minecraft_server_info(server_ip)

        if data is False:
            return await interaction.response.send_message(
                get_lang_by_address("utils.MinecraftServer.NotFound", lang)
            )

        motd = f"```{'\n'.join(data['motd'])}```" # type: ignore
        server_info = get_lang_by_address("utils.MinecraftServer.ServerIp", lang) + server_ip  # type: ignore
        version = get_lang_by_address("utils.MinecraftServer.version", lang) + data["version"]  # type: ignore
        players = f"{get_lang_by_address('utils.MinecraftServer.players', lang)}{data['players'][0]}/{data['players'][1]}"  # type: ignore

        embed = rich_embeds(
            Embed(
                title=f"{server_ip} {get_lang_by_address('utils.MinecraftServer.online', lang)}",
                description="\n".join([motd, server_info, version, players]),
            ),
            author,
            lang["main"],
        )

        return await interaction.response.send_message(embed=embed)


# async def setup(bot):
#     await bot.add_cog(MinecraftCog(bot))
#     await bot.add_cog(UtilsCog(bot))
