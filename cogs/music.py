import asyncio
import logging
from typing import List
from unittest import result
from discord import Embed, Interaction, Message, app_commands
from discord.ext.commands import GroupCog, Cog, Bot
from discord.ui import Select
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

        suggests_channel = self.bot.get_channel(957341782721585223)
        lang = await return_user_lang(self, interaction.user.id)
        
        await suggests_channel.send(f"{interaction.user} suggested {song} \n User ID: {interaction.user.id}, Guild ID: {interaction.guild.id}")
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
        
    async def _connect1(self, interaction : Interaction, lang : dict, cnt_cmd : bool) -> wavelink.Player or None or str("error"):
        if not interaction.user.voice: # author not in voice channel
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["user_no_voice"])
            return "error"
        if interaction.guild.voice_client:
            if interaction.guild.voice_client.channel is not interaction.user.voice.channel:
                await interaction.response.send_message(lang["music"]["voice_client"]["error"]["playing_in_another_channel"])
                return "error"
            elif interaction.guild.voice_client.channel is interaction.user.voice.channel and cnt_cmd:
                await interaction.response.send_message(lang["music"]["voice_client"]["error"]["already_connected"])
            return interaction.guild.voice_client
        return None
    
    async def _connect2(self, interaction : Interaction, lang : dict, cnt_cmd : bool = False) -> wavelink.Player:
        player = await self._connect1(interaction, lang, cnt_cmd)
        if player == "error":
            return
        elif player is None:
            if cnt_cmd:
                await interaction.response.send_message(lang["music"]["voice_client"]["status"]["connecting"])
            player = await interaction.user.voice.channel.connect(self_deaf = True, cls = wavelink.Player)
            if cnt_cmd:
                await interaction.edit_original_message(
                    content = lang["music"]["voice_client"]["status"]["connected"]
                )
        return player
        
    async def _disconnect1(self, interaction : Interaction, lang : dict) -> None or True:
        if not interaction.user.voice: # author not in voice channel
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["user_no_voice"])
        if not interaction.guild.voice_client: # bot didn't even connect lol
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["not_connected"])
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["playing_in_another_channel"])
        return True
    
    async def _disconnect2(self, interaction : Interaction, lang : dict) -> None or True:
        if not result:
            return
        await interaction.response.send_message(lang["music"]["voice_client"]["status"]["disconnecting"])
        await interaction.guild.voice_client.disconnect()
        await interaction.edit_original_message(
            content = lang["music"]["voice_client"]["status"]["disconnected"]
        )
        return True

    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "connect")
    async def connect(self, interaction : Interaction):
        """
        Connect to a voice channel.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        await self._connect2(interaction, lang, True)
        return
        
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "disconnect")
    async def disconnect(self, interaction : Interaction):
        """
        Disconnect from a voice channel.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        await self._disconnect2(interaction, lang)
        return
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "play")
    async def play(self, interaction : Interaction, query : str):
        """
        Play a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        player : wavelink.Player = await self._connect2(interaction, lang)
        track : wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(query = query, return_first=True)

        await player.play(track)
        return await interaction.response.send_message(lang["music"]["voice_client"]["status"]["playing"])
    
    @app_commands.checks.cooldown(1, 1.75, key = user_cooldown_check)
    @app_commands.command(name = "search")
    async def search(self, interaction : Interaction, query : str):
        """
        Search for a song.
        """

        lang = await return_user_lang(self, interaction.user.id)

        player : wavelink.Player = await self._connect2(interaction, lang)
        tracks : List[wavelink.Track] = await wavelink.YouTubeTrack.search(query = query)
        
        embed = Embed(
            title = lang["music"]["misc"]["result"],
            description = "",
            color = 0x00ff00
        )
        counter = 1
        
        select_menu = Select()
        
        for track in tracks:
            embed.description += f"{counter}. {track.title}\n"
            select_menu.add_option(label = f"{counter}. {track.title}", value = counter)
            counter += 1
            
        await interaction.response.send_message(embed = embed, view = select_menu.view)
        
        def check(msg : Message):
            return msg.author == interaction.user and msg.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return await interaction.edit_original_message("Your request has timed out.")
        
        track = tracks[int(msg.content) - 1]
        await interaction.edit_original_message(f"You have selected {track.title}.")
        await player.play(track)
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "pause")
    async def pause(self, interaction : Interaction):
        """
        Pause a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
        await vcl.pause()
        return await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["paused"])
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "resume")
    async def resume(self, interaction : Interaction):
        """
        Resume a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
        await vcl.resume()
        return await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["resumed"])