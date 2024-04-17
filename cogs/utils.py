"""
Utilities for the bot.
"""

from discord import AllowedMentions, Embed, Interaction, Member, User
from discord.app_commands import checks, command, guild_only
from discord.ext.commands import Cog, GroupCog
from discord.ui import Select, View

from akatsuki_du_ca import AkatsukiDuCa
from cogs.music import Player
from config import config
from modules.database import set_user_lang
from modules.lang import get_lang, lang_list
from modules.log import logger
from modules.minecraft import get_minecraft_server
from modules.misc import GuildTextableChannel, rich_embed, user_cooldown_check
from modules.osu import get_player


class ChangeLang(Select):
    """
    Change language Select menu class
    """

    def __init__(self, author: User | Member):
        self.author = author

        super().__init__(placeholder = "Choose language")

    async def callback(self, interaction: Interaction):
        await set_user_lang(interaction.user.id, self.values[0])

        await interaction.response.send_message("\U0001f44c", ephemeral = True)
        return


class UtilsCog(Cog):
    """
    Utilities commands for user.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        logger.info("Utilities Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Utilities Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "osu")
    async def osu(self, interaction: Interaction, username: str):
        """
        Get osu! stats for a user
        """

        author = interaction.user

        lang = await get_lang(author.id)

        player = await get_player(username)
        if not player:
            return await interaction.response.send_message(
                lang("utils.osu.player_not_found")
            )

        assert player.statistics

        description = lang("utils.osu.stats.description") % (
            player.statistics.global_rank,
            player.statistics.pp,
        )

        embed = rich_embed(
            Embed(
                title = lang("utils.osu.stats.title") % player.username,
                description = description,
            ).set_thumbnail(url = player.avatar_url).set_author(
                name = "osu! user data",
                icon_url =
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png",
            ),
            author,
            lang,
        )

        return await interaction.response.send_message(embed = embed)

    @checks.cooldown(1, 2.5, key = user_cooldown_check)
    @command(name = "bugreport")
    async def bugreport(
        self, interaction: Interaction[AkatsukiDuCa], bug_description: str
    ):
        """
        Report a bug. Use wisely
        """

        lang = await get_lang(interaction.user.id)

        bug_channel = interaction.client.get_channel(config.bot.channels.bug)

        await interaction.response.send_message(
            lang("utils.bug_report.success")
        )

        assert isinstance(bug_channel, GuildTextableChannel)

        await bug_channel.send(
            f"{interaction.user} báo lỗi: {bug_description}",
            allowed_mentions = AllowedMentions(
                users = False, roles = False, everyone = False
            ),
        )
        return await bug_channel.send(f"User ID: {interaction.user.id}")

    @checks.cooldown(1, 30, key = user_cooldown_check)
    @command(name = "change_language")
    async def change_language(self, interaction: Interaction):
        """
        Start an interactive language change session. hehe
        """

        lang = await get_lang(interaction.user.id)

        select_menu = ChangeLang(interaction.user)

        for option in lang_list:
            select_menu.add_option(label = option, value = option)

        view = View(timeout = 30).add_item(select_menu)

        await interaction.response.send_message(
            content = lang("utils.change_language"),
            view = view,
            ephemeral = True
        )

        if await view.wait():
            item = view.children[0]
            assert isinstance(item, ChangeLang)
            item.disabled = True
            return await interaction.edit_original_response(view = view)

    @checks.cooldown(1, 2, key = user_cooldown_check)
    @command(name = "ping")
    async def ping_bot(self, interaction: Interaction):
        """
        Check and send bot ping/latency
        """

        response = f"\U0001f3d3 Pong! `{round(interaction.client.latency * 1000)}ms`"

        voice_client = interaction.client.voice_clients

        if interaction.guild and isinstance(voice_client, Player):
            response += (
                f"\n\U0001f3b5 Music latency: `{voice_client.ping}ms`"
            )

        await interaction.response.send_message(content = response)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "server_info")
    @guild_only()
    async def server_info(self, interaction: Interaction):
        """
        Send server info
        """

        assert interaction.guild
        guild = interaction.guild
        embed = Embed(title = "Server Info", description = "")

        embed.add_field(name = "Server Name", value = guild.name)
        embed.add_field(name = "Server ID", value = guild.id)
        embed.add_field(name = "Server Owner", value = guild.owner)
        embed.add_field(
            name = "Server Age",
            value = f"<t:{int(guild.created_at.timestamp())}:D>"
        )
        embed.add_field(
            name = "Server Member Count", value = guild.member_count
        )

        embed.set_thumbnail(url = guild.icon.url if guild.icon else None)

        await interaction.response.send_message(
            embed = rich_embed(
                embed, interaction.user, await get_lang(interaction.user.id)
            )
        )

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "user_info")
    @guild_only()
    async def user_info(
        self, interaction: Interaction, user: Member | None = None
    ):
        """
        Send user info
        """

        if not user:
            assert isinstance(interaction.user, Member)
            user = interaction.user
        assert user.joined_at

        embed = Embed(title = "User Info", description = "")

        embed.add_field(name = "User Name", value = user.name)
        embed.add_field(name = "User ID", value = user.id)
        embed.add_field(name = "User Status", value = user.status)
        embed.add_field(
            name = "User Joined Date",
            value = f"<t:{int(user.joined_at.timestamp())}:D>"
        )
        embed.add_field(
            name = "User Creation Date",
            value = f"<t:{int(user.created_at.timestamp())}:D>"
        )
        embed.add_field(
            name = "User Roles",
            value = ", ".join([
                role.mention for role in user.roles if not role.is_default()
            ]) if len(user.roles) != 1 else "No Roles",
            inline = False,
        )
        embed.set_thumbnail(url = user.avatar.url if user.avatar else None)

        await interaction.response.send_message(
            embed = rich_embed(
                embed, user, await get_lang(interaction.user.id)
            ),
            allowed_mentions = AllowedMentions(
                everyone = False, users = False, roles = False
            ),
        )

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "avatar")
    @guild_only()
    async def avatar(
        self, interaction: Interaction, user: Member | None = None
    ):
        """
        Get a user avatar
        """

        assert isinstance(interaction.user, Member)
        if not user:
            user: Member = interaction.user

        assert user

        embed = rich_embed(
            Embed(title = "Avatar"), interaction.user, await
            get_lang(interaction.user.id)
        )

        embed.set_image(url = user.avatar.url if user.avatar else None)
        await interaction.response.send_message(embed = embed)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "server_icon")
    @guild_only()
    async def server_icon(self, interaction: Interaction):
        """
        Get a user avatar
        """

        assert interaction.guild

        embed = rich_embed(
            Embed(title = "Server Icon", ),
            interaction.user,
            await get_lang(interaction.user.id),
        )

        embed.set_image(
            url = interaction.guild.icon.url if interaction.guild.
            icon else None
        )
        await interaction.response.send_message(embed = embed)


class MinecraftCog(GroupCog, name = "minecraft"):
    """
    Minecraft related commands.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        super().__init__()

    async def cog_load(self) -> None:
        logger.info("Minecraft Cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Minecraft Cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "java_server")
    async def java_server(self, interaction: Interaction, server_ip: str):
        """
        Find info about a Minecraft Java server
        """

        lang = await get_lang(interaction.user.id)

        await interaction.response.defer()

        data = await get_minecraft_server(server_ip)

        if not data:
            return await interaction.response.send_message(
                lang("utils.minecraft.server.not_found")
            )

        motd = "```" + "\n".join(data.motd) + "```"
        server_info = lang("utils.minecraft.server_ip") % server_ip
        version = lang("utils.minecraft.server.version") % data.version
        players = lang("utils.minecraft.server.players") % (
            data.players.online,
            data.players.max,
        )

        return await interaction.response.send_message(
            embed = rich_embed(
                Embed(
                    title = lang("utils.minecraft.server.online") % server_ip,
                    description = "\n".join([
                        motd, server_info, version, players
                    ]),
                ),
                interaction.user,
                lang,
            ),
            ephemeral = True,
        )
