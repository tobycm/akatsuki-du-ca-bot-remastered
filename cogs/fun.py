from discord import Object, User, app_commands, Interaction
from discord.ext.commands import Cog, Bot

from modules.checks_and_utils import cooldown_check, return_user_lang
from modules.embed_process import rich_embeds
from modules.gif_api import construct_gif_embed

class Fun(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    def cog_load(self):
        print("loaded")
        
    @property
    def qualified_name(self):
        return ":joy:  Fun"

    def description(self):
        return "Fun commands that is sussy amogus"
        
    
    @app_commands.checks.cooldown(1, 1, key = cooldown_check)
    @app_commands.command(name = "slap")
    @app_commands.guilds(Object(912563175919083571))
    async def slap(self, interaction: Interaction, target : User):
        """
        Slap someone xD
        """
        
        if target is self.bot.user:
            return await interaction.response.send_message("etou...", ephemeral = True)
        
        method = "slap"
        author = interaction.user
        lang = await return_user_lang(self, author.id)
        
        embed = await construct_gif_embed(
            f"{author.name}#{author.discriminator}",
            f"{target.name}#{target.discriminator}",
            method = method,
            lang = lang["gif"])
        
        await interaction.channel.send(embed = rich_embeds(embed, author, lang["main"]))
        return await interaction.response.send_message("Sent!", ephemeral = True)

# async def setup(bot: Bot) -> None:
#   await bot.add_cog(Fun(bot))