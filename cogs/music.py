import logging
from typing import List
from unittest import result
from discord import Color, Embed, Interaction, app_commands
from discord.ext.commands import GroupCog, Cog, Bot
from discord.ui import Select, View
import wavelink

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
        bot.music_channel : dict = {}
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
        
    @Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason: str):
        """
        Event fired when a track ends.
        """

        await self.bot.music_channel[player.guild.id].send(f"{track.title} has ended")
        if player.queue.is_empty:
            return await player.disconnect()
        next_track : wavelink.YouTubeTrack = await player.queue.get_wait()
        await player.play(next_track)
        
    @Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        """
        Event fired when a track starts.
        """

        embed = Embed(
            title = "Now playing",
            description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            color = Color.random()
        ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg")
        await self.bot.music_channel[player.guild.id].send(embed = embed)
        
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
        
        self.bot.music_channel[interaction.guild.id] = interaction.channel
        player : wavelink.Player = await self._connect2(interaction, lang)
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["searching"])
        track : wavelink.YouTubeTrack = await wavelink.YouTubeTrack.search(query = query, return_first=True)

        await player.queue.put_wait(track)
        if not player.is_playing():
            await player.play(await player.queue.get_wait())
        await interaction.edit_original_message(embed = rich_embeds(
            Embed(
                title = lang["music"]["misc"]["action"]["queue"]["added"],
                description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"),
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

        self.bot.music_channel[interaction.guild.id] = interaction.channel
        player : wavelink.Player = await self._connect2(interaction, lang)
        await interaction.response.send_message(lang["music"]["misc"]["action"]["music"]["searching"])
        
        tracks : List[wavelink.Track] = await wavelink.YouTubeTrack.search(query = query)
        
        class music_select(Select):
            def __init__(self) -> None:
                super().__init__(placeholder = "Make your music selection")
        
            async def callback(self, interaction : Interaction):
                track = tracks[int(self.values[0]) - 1]
                await interaction.response.send_message(content = f"You have selected {track.title}.")
                await player.queue.put_wait(track)
                if not player.is_playing():
                    await player.play(await player.queue.get_wait())
                    await interaction.channel.send(embed = rich_embeds(
                        Embed(
                            title = lang["music"]["misc"]["action"]["queue"]["added"],
                            description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
                        ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"),
                        interaction.user,
                        lang["main"]
                    ))
                return
        
        embed = Embed(
            title = lang["music"]["misc"]["result"],
            description = "",
            color = 0x00ff00
        )
        counter = 1
        
        select_menu : music_select = music_select()
        view = View(timeout = 30)
        
        for track in tracks:
            if counter == 6:
                break
            embed.description += f"{counter}. {track.title}\n"
            select_menu.add_option(label = f"{counter}. {track.title}", value = counter)
            counter += 1
            
        view.add_item(select_menu)
            
        await interaction.edit_original_message(content = lang["music"]["misc"]["result"], embed = embed, view = view)

        if await view.wait() and view.is_finished():
            view.children[0].disabled = True
            return await interaction.edit_original_message(view = view)

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
    
    @app_commands.checks.cooldown(1, 1.5, key = user_cooldown_check)
    @app_commands.command(name = "skip")
    async def skip(self, interaction : Interaction):
        """
        Skip a song
        """
        
        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
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
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
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
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
        if vcl.queue.is_empty:
            return await interaction.response.send_message(lang["music"]["misc"]["action"]["error"]["no_queue"])
        
        embed = rich_embeds(
            Embed(
                title = lang["music"]["misc"]["queue"],
                description = "",
            ),
            interaction.user,
            lang["main"]
        )
        counter = 1
        for track in vcl.queue:
            embed.description += f"{counter}. {track.title}\n"
            counter += 1
        return await interaction.response.send_message(embed = embed)
    
    @app_commands.checks.cooldown(1, 1.25, key = user_cooldown_check)
    @app_commands.command(name = "nowplaying")
    async def nowplaying(self, interaction : Interaction):
        """
        Show the now playing song.
        """

        lang = await return_user_lang(self, interaction.user.id)
        
        vcl : wavelink.Player = await self._connect2(interaction, lang)
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