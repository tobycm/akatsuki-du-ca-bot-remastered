"""
Fun cog for the bot.
"""

from random import choice, randint
from string import ascii_letters

from discord import ButtonStyle, Embed, File, Interaction, Member
from discord.app_commands import checks, command, guild_only
from discord.ext.commands import Cog, GroupCog
from discord.ui import View, Button

from akatsuki_du_ca import AkatsukiDuCa
from config import config
from modules.database import get_user_lang
from modules.exceptions import LangNotAvailable
from modules.gif import get_gif_url
from modules.lang import get_lang
from modules.misc import GuildTextableChannel, rich_embed, user_cooldown_check
from modules.quote import get_quote
from modules.waifu import random_image


class GIFCog(GroupCog, name = "gif"):
    """
    GIF related commands.
    """

    @staticmethod
    async def _gif(interaction: Interaction, target: Member):
        assert isinstance(interaction.channel, GuildTextableChannel)
        assert isinstance(interaction.user, Member)
        assert interaction.command

        if target is interaction.client.user:
            return await interaction.response.send_message(
                "etou...", ephemeral = True
            )

        lang = await get_lang(interaction.user.id)
        action = interaction.command.name

        await interaction.channel.send(
            embed = rich_embed(
                Embed(
                    title = lang(f"gif.{action}.title"),
                    description = lang(f"gif.{action}.text") %
                    (interaction.user.mention, target.mention)
                ).set_image(
                    url = await get_gif_url(action, config.api.tenor.key)
                ),
                interaction.user,
                lang,
            )
        )
        return await interaction.response.send_message(
            "Sent!", ephemeral = True
        )

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Fun cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Fun cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "slap")
    @guild_only()
    async def slap(self, interaction: Interaction, target: Member) -> None:
        """
        Slap someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "hug")
    @guild_only()
    async def hug(self, interaction: Interaction, target: Member):
        """
        Hug someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "pat")
    @guild_only()
    async def pat(self, interaction: Interaction, target: Member):
        """
        Pat someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "punch")
    @guild_only()
    async def punch(self, interaction: Interaction, target: Member):
        """
        Punch someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "kick")
    @guild_only()
    async def kick(self, interaction: Interaction, target: Member):
        """
        Kick someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "bite")
    @guild_only()
    async def bite(self, interaction: Interaction, target: Member):
        """
        Bite someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "cuddle")
    @guild_only()
    async def cuddle(self, interaction: Interaction, target: Member):
        """
        Cuddle someone xD
        """

        await self._gif(interaction, target)

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "poke")
    @guild_only()
    async def poke(self, interaction: Interaction, target: Member):
        """
        Poke someone xD
        """

        await self._gif(interaction, target)


class FunCog(Cog):
    """
    Other fun commands.
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
        super().__init__()

    @checks.cooldown(1, 5, key = user_cooldown_check)
    @command(name = "alarm")
    @guild_only()
    async def alarm(self, interaction: Interaction):
        """
        Send an alarm >:)
        """

        lang_option = await get_user_lang(interaction.user.id)
        if lang_option != "vi-vn":
            raise LangNotAvailable

        assert isinstance(interaction.channel, GuildTextableChannel)

        await interaction.response.send_message(
            "Đang gửi...", ephemeral = True
        )
        if randint(1, 50) == 25:
            # bro got lucky
            await interaction.channel.send(
                content =
                "Bạn may mắn thật đấy, bạn được Ban Mai gọi dậy nè :))",
                file = File("assets/banmai.mp4"),
            )
        else:
            await interaction.channel.send(
                content =
                "Ngủ nhiều là không tốt đâu đó nha :D \n - Du Ca said - ",
                file = File("assets/duca.mp4"),
            )
        return await interaction.edit_original_response(content = "Đã gửi :D")

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "waifu")
    async def waifu(self, interaction: Interaction):
        """
        Wan sum waifu?
        """
        lang = await get_lang(interaction.user.id)

        image = await random_image()

        return await interaction.response.send_message(
            embed = rich_embed(
                Embed(
                    title = "Waifu",
                    description = lang("fun.waifu") % image,
                ),
                interaction.user,
                lang,
            ).set_image(url = str(image))
        )

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "freenitro")
    @guild_only()
    async def freenitro(self, interaction: Interaction):
        """
        OMG free NiTrO!!1! gotta claim fast
        """

        code = ""
        for _ in range(0, 23):
            code += choice(ascii_letters)

        lang = await get_lang(interaction.user.id)

        riel = f"[discord.gift/{code}](https://akatsukiduca.tk/verify-nitro?key={code}&id={interaction.user.id})"

        embed = Embed(
            title = lang("fun.free_nitro.title"),
            description = lang("fun.free_nitro.description") % riel,
            color = 0x2F3136,
        )
        embed.set_image(url = "https://i.ibb.co/5LDTWSj/freenitro.png")
        await interaction.response.send_message(
            lang("fun.free_nitro.success"), ephemeral = True
        )

        view = View(timeout = 600)
        view.add_item(
            Button(style = ButtonStyle.blurple, label = "Claim", url = riel)
        )

        assert isinstance(interaction.channel, GuildTextableChannel)
        return await interaction.channel.send(riel, embed = embed, view = view)

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "quote")
    async def quote(self, interaction: Interaction):
        """
        A good quote for the day
        """

        quote = await get_quote()

        return await interaction.response.send_message(
            embed = rich_embed(
                Embed(title = quote.author, description = quote.quote),
                interaction.user,
                await get_lang(interaction.user.id),
            ),
            ephemeral = True,
        )
