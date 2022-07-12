from discord import Interaction, app_commands
from discord.ext.commands import GroupCog

from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.log_utils import command_log

class RadioMusic(GroupCog, name = "radio"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.checks.cooldown(1, 10, key = user_cooldown_check)
    @app_commands.command(name = "suggest")
    async def suggest(self, interaction : Interaction, song : str):
        """
        Got new songs for my radio? Thank you so much ♥
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        
        suggests_channel = self.bot.get_channel(957341782721585223)
        lang = await return_user_lang(self, author.id)
        
        await suggests_channel.send(f"{author} suggested {song} \n User ID: {author.id}, Guild ID: {author.guild.id}")
        await interaction.response.send_message(lang["music"]["SuggestionSent"])
        