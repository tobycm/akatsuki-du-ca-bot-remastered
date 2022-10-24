"""
Fun cog for the bot.
"""

from random import randint, choice
from string import ascii_letters
from time import time

from discord import Embed, Member, Interaction, File
from discord.app_commands import command, checks
from discord.ext.commands import GroupCog, Cog, Bot

from modules.checks_and_utils import user_cooldown_check, return_user_lang
from modules.database_utils import get_user_lang
from modules.embed_process import rich_embeds
from modules.exceptions import LangNotAvailable
from modules.gif_api import construct_gif_embed

from modules.quote_api import get_quotes
from modules.waifu_api import get_waifu_image_url


class GIFCog(GroupCog, name="gif"):
    """
    GIF related commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    async def _gif(self, itr: Interaction, target: Member):
        method = itr.command.name
        author = itr.user
        if target is self.bot.user:
            return await itr.response.send_message("etou...", ephemeral=True)

        lang = await return_user_lang(self.bot, author.id)

        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"]
        )

        await itr.channel.send(embed=rich_embeds(embed, author, lang["main"]))
        return await itr.response.send_message("Sent!", ephemeral=True)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="slap")
    async def slap(self, itr: Interaction, target: Member):
        """
        Slap someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="hug")
    async def hug(self, itr: Interaction, target: Member):
        """
        Hug someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="pat")
    async def pat(self, itr: Interaction, target: Member):
        """
        Pat someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="punch")
    async def punch(self, itr: Interaction, target: Member):
        """
        Punch someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="kick")
    async def kick(self, itr: Interaction, target: Member):
        """
        Kick someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="bite")
    async def bite(self, itr: Interaction, target: Member):
        """
        Bite someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="cuddle")
    async def cuddle(self, itr: Interaction, target: Member):
        """
        Cuddle someone xD
        """

        await self._gif(itr, target)

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="poke")
    async def poke(self, itr: Interaction, target: Member):
        """
        Poke someone xD
        """

        await self._gif(itr, target)

class FunCog(Cog):
    """
    Other fun commands.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @checks.cooldown(1, 5, key=user_cooldown_check)
    @command(name="alarm")
    async def alarm(self, itr: Interaction):
        """
        Send an alarm >:)
        """

        author = itr.user

        lang_option = await get_user_lang(self.bot.redis_ins, author.id)
        if lang_option != "vi-vn":
            raise LangNotAvailable

        await itr.response.send_message("Đang gửi...", ephemeral=True)
        if randint(1, 50) == 25:
            # bro got lucky
            await itr.channel.send(
                content="Bạn may mắn thật đấy, bạn được Ban Mai gọi dậy nè :))",
                file=File("assets/banmai.mp4")
            )
        else:
            await itr.channel.send(
                content="Ngủ nhiều là không tốt đâu đó nha :D \n - Du Ca said - ",
                file=File("assets/duca.mp4")
            )
        return await itr.edit_original_response(content="Đã gửi :D")

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="waifu")
    async def waifu(self, itr: Interaction):
        """
        Wan sum waifu?
        """

        author = itr.user
        lang = await return_user_lang(self.bot, author.id)

        (url, source) = await get_waifu_image_url()

        embed = rich_embeds(Embed(
            title="Waifu",
            description=f"{lang['fun']['waifu']}\n[Source]({source})"
        ),
            author,
            lang["main"])
        embed.set_image(url=url)
        return await itr.response.send_message(embed=embed)

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="freenitro")
    async def freenitro(self, itr: Interaction):
        """
        OMG free NITRO!!!! gotta claim fast
        """

        author = itr.user
        code = ""
        for _ in range(0, 23):
            code += choice(ascii_letters)

        lang = await return_user_lang(self.bot, author.id)

        embed = Embed(
            title=lang["fun"]["NitroFree"]["Title"],
            description=f"{lang['fun']['NitroFree']['Description']}\n[https://discord.gift/{code}](https://akatsukiduca.tk/verify-nitro?key={code}&id={author.id})",
            color=0x2F3136
        )
        embed.set_image(url="https://i.ibb.co/5LDTWSj/freenitro.png")
        await itr.response.send_message("Getting sweet free nitro for you <3", ephemeral=True)
        return await itr.channel.send(embed=embed)

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="quote")
    async def quote(self, itr: Interaction):
        """
        A good quote for the day
        """

        author = itr.user
        lang = await return_user_lang(self.bot, author.id)
        time_now = time()

        if (time_now - self.bot.quotes_added) > 900:
            self.bot.quotes = await get_quotes()
            self.bot.quotes_added = time_now

        quote = choice(self.bot.quotes)
        for author, quote in quote:

            return await itr.response.send_message(
                embed=rich_embeds(
                    Embed(
                        title=author,
                        description=quote
                    ),
                    author,
                    lang["main"]
                ),
                ephemeral=True
            )
