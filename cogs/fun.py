from random import randint, choice
from string import ascii_letters
from time import time
from discord import Embed, User, app_commands, Interaction, File
from discord.ext.commands import GroupCog, Bot, Cog

from modules.checks_and_utils import user_cooldown_check, return_user_lang
from modules.database_utils import get_user_lang
from modules.embed_process import rich_embeds
from modules.gif_api import construct_gif_embed
from modules.log_utils import command_log
from modules.quote_api import get_quotes
from modules.waifu_api import get_waifu_image_url

class GIFCog(GroupCog, name = "gif"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()
    
    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "slap")
    async def slap(self, interaction: Interaction, target : User):
        """
        Slap someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "hug")
    async def hug(self, interaction: Interaction, target : User):
        """
        Hug someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "pat")
    async def pat(self, interaction: Interaction, target : User):
        """
        Pat someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "punch")
    async def punch(self, interaction: Interaction, target : User):
        """
        Punch someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "kick")
    async def kick(self, interaction: Interaction, target : User):
        """
        Kick someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "bite")
    async def bite(self, interaction: Interaction, target : User):
        """
        Bite someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "cuddle")
    async def cuddle(self, interaction: Interaction, target : User):
        """
        Cuddle someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

    @app_commands.checks.cooldown(1, 1, key = user_cooldown_check)
    @app_commands.command(name = "poke")
    async def poke(self, interaction: Interaction, target : User):
        """
        Poke someone xD
        """
        
        method = interaction.command.name
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, method)
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            author,
            target,
            method,
            lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

class FunCog(Cog):
    def __init__(self, bot : Bot) -> None:
        self.bot = bot
        
    @app_commands.checks.cooldown(1, 5, key = user_cooldown_check)
    @app_commands.command(name = "alarm")
    async def alarm(self, interaction : Interaction):
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, "alarm")
        
        lang = await return_user_lang(self, author.id)
        lang_option = await get_user_lang(self.bot.redis_ins, author.id)
        if lang_option != "vi-vn":
            return await interaction.response.send_message(lang["main"]["NotAvailableLanguage"])
        
        if randint(1, 50) == 25:
            # bro got lucky
            await interaction.response.send_message("Đã gửi :D", ephemeral = True)
            return await interaction.channel.send(content = "Bạn may mắn thật đấy, bạn được Ban Mai gọi dậy nè :))", file = File("assets/banmai.mp4"))
        
        await interaction.response.send_message("Đã gửi :D", ephemeral = True)
        return await interaction.channel.send(content = "Ngủ nhiều là không tốt đâu đó nha :D \n - Du Ca said - ", file = File("assets/duca.mp4"))
        
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "waifu")
    async def waifu(self, interaction : Interaction):
        """
        Wan sum waifu?
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, "waifu")
        lang = await return_user_lang(self, author.id)
        
        (url, source) = await get_waifu_image_url()
        
        embed = rich_embeds(Embed(
            title="Waifu",
            description=f"{lang['fun']['waifu']}\n[Source]({source})"
            ),
                            author,
                            lang["main"])
        embed.set_image(url=url)
        return await interaction.channel.send(embed = embed)
    
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "freenitro")
    async def freenitro(self, interaction : Interaction):
        """
        OMG free NITRO!!1! gotta claim fast
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, "freenitro")
        
        code = ""
        for i in range(0, 23):
            code += choice(ascii_letters)
            
        lang = await return_user_lang(self, author.id)
        
        embed = Embed(
            title = lang["fun"]["NitroFree"]["Title"],
            description = f"{lang['fun']['NitroFree']['Description']}\n[https://discord.gift/{code}](http://akatsukiduca.ddns.net/redirect/api/js/nitro?key={code}&id={author.id})",
            color = 0x2F3136
        )
        embed.set_image(url = "https://i.ibb.co/5LDTWSj/freenitro.png")
        await interaction.response.send_message("Getting sweet free nitro for you <3", ephemeral = True)
        return await interaction.channel.send(embed = embed)
        
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "quote")
    async def quote(self, interaction : Interaction):
        """
        A good quote for the day
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, "quote")
        
        lang = await return_user_lang(self, author.id)
        time_now = time()
        
        if (time_now - self.bot.quotes_added) > 900:
            self.bot.quotes = await get_quotes()
            self.bot.quotes_added = time_now
            
        quote = choice(self.bot.quotes)
        for a, q in quote:
            author = a
            quote = q
            
        return await interaction.response.send_message(
            embed = rich_embeds(Embed(
                title = author,
                description = quote
            ),
            author,
            lang["main"]),
            ephemeral = True)

async def setup(bot):
    await bot.add_cog(FunCog(bot))
    print("Fun Cog loaded")
    await bot.add_cog(GifCog(bot))
    print("Gif Cog loaded")