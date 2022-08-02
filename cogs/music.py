import logging
from discord import Interaction, app_commands
from discord.ext.commands import GroupCog, Cog, Bot
import wavelink

from modules.checks_and_utils import return_user_lang, user_cooldown_check
from modules.log_utils import command_log
from modules.vault import get_lavalink_nodes

class RadioMusic(GroupCog, name = "radio"):
    def __init__(self, bot : Bot):
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
        
class MusicCog(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot : Bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """
        Connect to Lavalink nodes.
        """
        await self.bot.wait_until_ready()
        
        for node in get_lavalink_nodes():
            await wavelink.NodePool.create_node(
                bot = self.bot,
                host = node["host"],
                port = node["port"],
                password = node["password"]
            )

    @Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """
        Event fired when a node has finished connecting.
        """
        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Connected to {node.host}:{node.port}")

    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "connect")
    async def connect(self, interaction : Interaction):
        """
        Connect to a voice channel.
        """
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        lang = await return_user_lang(self, author.id)
        
        if not interaction.user.voice: # author not in voice channel
            return await interaction.response.send_message(lang["music"]["voice_client"]["error"]["user_no_voice"])
        if interaction.guild.voice_client.channel is interaction.user.voice.channel: # bot is already connected lmao
            return await interaction.response.send_message(lang["music"]["voice_client"]["error"]["already_connected"])
        elif interaction.guild.voice_client: # in another voice channel
            return await interaction.response.send_message(lang["music"]["voice_client"]["error"]["playing_in_another_channel"])
        
        await interaction.response.send_message(lang["music"]["voice_client"]["status"]["connecting"])
        await interaction.user.voice.channel.connect() 
        return await interaction.edit_original_message(
            content = lang["music"]["voice_client"]["status"]["connected"]
        )
