import re
import logging
from typing import List, Literal
from unittest import result
from discord import Color, Embed, Interaction, app_commands
from discord.ext.commands import GroupCog, Cog, Bot
from discord.ui import View
from wavelink import Track, YouTubePlaylist, YouTubeTrack, NodePool, Node

from models.music_models import added_a_track_embed, added_a_playlist_embed, custom_player, music_select, queue_page_select, make_queue_embed
from modules.checks_and_utils import return_user_lang, user_cooldown_check, seconds_to_time
from modules.embed_process import rich_embeds
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
            await NodePool.create_node(
                bot = self.bot,
                host = node["host"],
                port = node["port"],
                password = node["password"]
            )

    @Cog.listener()
    async def on_wavelink_node_ready(self, node: Node):
        """
        Event fired when a node has finished connecting.
        """
        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Connected to {node.host}:{node.port}")
        
    @Cog.listener()
    async def on_wavelink_websocket_closed(self, player : custom_player, reason : str, code : int):
        """
        Event fired when the Node websocket has been closed by Lavalink.
        """
        
        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Disconnected from {player.node.host}:{player.node.port}")
        bot_logger.info(f"Reason: {reason} | Code: {code}")
        
    @Cog.listener()
    async def on_wavelink_track_end(self, player: custom_player, track: Track, reason: str):
        """
        Event fired when a track ends.
        """

        await player.text_channel.send(f"{track.title} has ended")
        if player.queue.is_empty:
            player.text_channel = None
            player.loop_mode = None
            return await player.disconnect()
        next_track : YouTubeTrack = await player.queue.get_wait()
        await player.play(next_track)
        
    @Cog.listener()
    async def on_wavelink_track_start(self, player: custom_player, track: Track):
        """
        Event fired when a track starts.
        """

        embed = Embed(
            title = "Now playing",
            description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            color = Color.random()
        ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg")
        try:
            if player.loop_mode == "song":
                player.queue.put_at_front(track)
            elif player.loop_mode == "queue":
                await player.queue.put_wait(track)
        except AttributeError:
            pass
        await player.text_channel.send(embed = embed)
        
    @Cog.listener()
    async def on_wavelink_track_exception(self, player: custom_player, track: Track, error):
        """
        Event fired when a track encounters an exception.
        """

        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Track {track.title} encountered an exception: {error}")
        print(type(error))
        
    @Cog.listener()
    async def on_wavelink_track_stuck(self, player : custom_player, track : Track, *args):
        """
        Event fired when a track is stuck.
        """

        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Track {track.title} is stuck")
        await player.text_channel.send(f"{track.title} is stuck")
                
    async def connect_check(self, interaction : Interaction, lang : dict, cnt_cmd : bool) -> custom_player or None or str("error"):
        usr_voice = interaction.user.voice
        if not usr_voice: # author not in voice channel
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["user_no_voice"])
            return "error"
        vcl = interaction.guild.voice_client
        if vcl:
            if vcl.channel is usr_voice.channel and cnt_cmd:
                await interaction.response.send_message(lang["music"]["voice_client"]["error"]["already_connected"])
        return vcl
    
    async def _connect(self, interaction : Interaction, lang : dict, cnt_cmd : bool = False) -> custom_player:
        player = await self.connect_check(interaction, lang, cnt_cmd)
        if player == "error":
            return
        elif player is None:
            if cnt_cmd:
                await interaction.response.send_message(lang["music"]["voice_client"]["status"]["connecting"])
            player = await interaction.user.voice.channel.connect(self_deaf = True, cls = custom_player)
            if cnt_cmd:
                await interaction.edit_original_message(
                    content = lang["music"]["voice_client"]["status"]["connected"]
                )
        return player
        
    async def disconnect_check(self, interaction : Interaction, lang : dict) -> None or True:
        if not interaction.user.voice: # author not in voice channel
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["user_no_voice"])
        if not interaction.guild.voice_client: # bot didn't even connect lol
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["not_connected"])
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message(lang["music"]["voice_client"]["error"]["playing_in_another_channel"])
        return True
    
    async def _disconnect(self, interaction : Interaction, lang : dict) -> None or True:
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
        
        await self._connect(interaction, lang, True)
        return
        
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "disconnect")
    async def disconnect(self, interaction : Interaction):
        """
        Disconnect from a voice channel.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        await self._disconnect(interaction, lang)
        return
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "play")
    async def play(self, interaction : Interaction, query : str):
        """
        Play a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        player : custom_player = await self._connect(interaction, lang)
        player.text_channel = interaction.channel
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["searching"])
        
        try:
            track : YouTubeTrack = await YouTubeTrack.search(query = query, return_first=True)
            playlist = False
        except:
            playlist : YouTubePlaylist = await YouTubePlaylist.search(query = query)
        
        if playlist:
            for track in playlist.tracks:
                await player.queue.put_wait(track)
                if not player.is_playing():
                    await player.play(await player.queue.get_wait())
            await interaction.edit_original_message(content = "", embed = rich_embeds(
                added_a_playlist_embed(playlist, lang, query),
                interaction.user,
                lang["main"]
            ))
            return
            
        await player.queue.put_wait(track)
        if not player.is_playing():
            await player.play(await player.queue.get_wait())
        await interaction.edit_original_message(content = "", embed = rich_embeds(
            added_a_track_embed(track, lang),
            interaction.user,
            lang["main"]
        ))
    
    @app_commands.checks.cooldown(1, 1.75, key = user_cooldown_check)
    @app_commands.command(name = "search")
    async def search(self, interaction : Interaction, query : str):
        """
        Search for a song.
        """

        lang = await return_user_lang(self, interaction.user.id)

        player : custom_player = await self._connect(interaction, lang)
        player.text_channel = interaction.channel
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["searching"])
        
        tracks : List[Track] = await YouTubeTrack.search(query = query)
        tracks = tracks[:5]
        embed = Embed(
            title = lang["music"]["misc"]["result"],
            description = "",
            color = 0x00ff00
        )
        counter = 1
        
        select_menu : music_select = music_select(tracks, player, lang)
        view = View(timeout = 30)
        
        for track in tracks:
            if counter == 6:
                break
            if len(track.title) > 50:
                title = track.title[:50] + "..."
            else:
                title = track.title
            
            embed.description += f"{counter}. [{track.title}]({track.uri})\n"
            select_menu.add_option(label = f"{counter}. {title}", value = counter)
            counter += 1
            
        view.add_item(select_menu)
            
        await interaction.edit_original_message(content = lang["music"]["misc"]["result"], embed = embed, view = view)

        if await view.wait():
            view.children[0].disabled = True
            return await interaction.edit_original_message(view = view)

    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "pause")
    async def pause(self, interaction : Interaction):
        """
        Pause a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        await vcl.pause()
        return await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["paused"])
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "resume")
    async def resume(self, interaction : Interaction):
        """
        Resume a song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        await vcl.resume()
        return await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["resumed"])
    
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "skip")
    async def skip(self, interaction : Interaction):
        """
        Skip a song
        """
        
        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        await vcl.stop()
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["skipped"])
        return
    
    @app_commands.checks.cooldown(1, 2, key = user_cooldown_check)
    @app_commands.command(name = "stop")
    async def stop(self, interaction : Interaction):
        """
        Stop playing music.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        if not vcl.queue.is_empty:
            vcl.queue.clear()
        await vcl.stop()
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["stopped"])
    
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "queue")
    async def queue(self, interaction : Interaction):
        """
        Show the queue.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        if vcl.queue.is_empty:
            return await interaction.response.send_message(lang["music"]["misc"]["action"]["error"]["no_queue"])
        
        queue_embeds = make_queue_embed(vcl.queue, lang)
        if len(queue_embeds) > 1:
            select_menu : queue_page_select = queue_page_select(len(queue_embeds), queue_embeds, lang, interaction)
            for i in range(len(queue_embeds)):
                select_menu.add_option(label = i + 1, value = i + 1)
            view = View(timeout = 60).add_item(select_menu)
        else:
            view = None
        
        await interaction.response.send_message(
            embed = rich_embeds(
                queue_embeds[0],
                interaction.user,
                lang["main"]
            ),
            view = view if view is not None else None
        )
        
        if await view.wait():
            view.children[0].disabled = True
            await interaction.edit_original_message(view = view)
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "nowplaying")
    async def nowplaying(self, interaction : Interaction):
        """
        Show the now playing song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        if not vcl.is_playing():
            return await interaction.response.send_message(lang["music"]["misc"]["action"]["error"]["no_music"])
        
        embed = rich_embeds(
            Embed(
                title = lang["music"]["misc"]["now_playing"],
                description = f"[**{vcl.track.title}**]({vcl.track.uri}) - {vcl.track.author}\nDuration: {seconds_to_time(vcl.position)}/{seconds_to_time(vcl.track.duration)}",
            ),
            interaction.user,
            lang["main"]
        )
        return await interaction.response.send_message(embed = embed)
    
    @app_commands.checks.cooldown(1, 1.75, key = user_cooldown_check)
    @app_commands.command(name = "clear_queue")
    async def clear_queue(self, interaction : Interaction):
        """
        Clear the queue
        """
        
        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        if vcl.queue.is_empty:
            return await interaction.response.send_message(lang["music"]["misc"]["action"]["error"]["no_queue"])
        
        vcl.queue.clear()
        await interaction.response.send_message(lang["music"]["misc"]["action"]["queue"]["cleared"])
        
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "loop")
    async def loop(self, interaction : Interaction, mode : Literal["off", "queue", "song"]):
        """
        Loop queue, song or turn loop off
        """
        
        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : custom_player = await self._connect(interaction, lang)
        if mode == "song":
            vcl.queue.put_at_front(vcl.track)
        elif mode == "off" and vcl.loop_mode == "song":
            await vcl.queue.get_wait()
        vcl.loop_mode = mode if mode != "off" else None
            
        await interaction.response.send_message(lang["music"]["misc"]["action"]["loop"][mode])