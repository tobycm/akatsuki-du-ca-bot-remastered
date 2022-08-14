"""
This is the music cog.
"""

import logging
from typing import List, Literal
from discord import Color, Embed, Interaction, app_commands
from discord.ext.commands import GroupCog, Cog, Bot
from discord.ui import View
from wavelink import Track, YouTubePlaylist, YouTubeTrack, NodePool, Node

from models.music_models import Player, NewPlaylist, MusicSel, PageSel, NewTrack, make_queue
from modules.checks_and_utils import return_user_lang, user_cooldown_check, seconds_to_time
from modules.embed_process import rich_embeds
from modules.vault import get_lavalink_nodes


class RadioMusic(GroupCog, name="radio"):
    """
    Radio commands for bot
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()

    @app_commands.checks.cooldown(1, 10, key=user_cooldown_check)
    @app_commands.command(name="suggest")
    async def suggest(self, itr: Interaction, song: str):
        """
        Got new songs for my radio? Thank you so much ♥
        """

        suggests_channel = self.bot.get_channel(957341782721585223)
        lang = await return_user_lang(self, itr.user.id)

        await suggests_channel.send(
            f"{itr.user} suggested {song} \n User ID: {itr.user.id}, Guild ID: {itr.guild.id}"
        )
        await itr.response.send_message(
            lang["music"]["SuggestionSent"]
        )


class MusicCog(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: Bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """
        Connect to Lavalink nodes.
        """
        await self.bot.wait_until_ready()

        for node in get_lavalink_nodes():
            await NodePool.create_node(
                bot=self.bot,
                host=node["host"],
                port=node["port"],
                password=node["password"]
            )

    @Cog.listener()
    async def on_wavelink_node_ready(self, node: Node):
        """
        Event fired when a node has finished connecting.
        """
        bot_logger = logging.getLogger('discord')
        bot_logger.info(f"Connected to {node.host}:{node.port}")

    @Cog.listener()
    async def on_wavelink_websocket_closed(self, player: Player, reason: str, code: int):
        """
        Event fired when the Node websocket has been closed by Lavalink.
        """

        bot_logger = logging.getLogger('discord')
        bot_logger.info(
            f"Disconnected from {player.node.host}:{player.node.port}")
        bot_logger.info(f"Reason: {reason} | Code: {code}")

    @Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: Track, *args):
        """
        Event fired when a track ends.
        """

        await player.text_channel.send(f"{track.title} has ended")
        if player.queue.is_empty:
            player.text_channel = None
            player.loop_mode = None
            return await player.disconnect()
        next_track: YouTubeTrack = await player.queue.get_wait()
        await player.play(next_track)

    @Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: Track):
        """
        Event fired when a track starts.
        """

        embed = Embed(
            title="Now playing",
            description=f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            color=Color.random()
        ).set_thumbnail(url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg")
        try:
            if player.loop_mode == "song":
                player.queue.put_at_front(track)
            elif player.loop_mode == "queue":
                await player.queue.put_wait(track)
        except AttributeError:
            pass
        await player.text_channel.send(embed=embed)

    @Cog.listener()
    async def on_wavelink_track_exception(self, player: Player, track: Track, error):
        """
        Event fired when a track encounters an exception.
        """

        bot_logger = logging.getLogger('discord')
        bot_logger.info(
            f"Track {track.title} encountered an exception: {error}. Guild: {player.guild.id}")
        print(type(error))

    @Cog.listener()
    async def on_wavelink_track_stuck(self, player: Player, track: Track, *args):
        """
        Event fired when a track is stuck.
        """

        bot_logger = logging.getLogger('discord')
        bot_logger.info(
            f"Track {track.title} is stuck. Guild: {player.guild.id}")
        await player.text_channel.send(f"{track.title} is stuck")

    async def connect_check(self, itr: Interaction, lang: dict, cnt_cmd: bool) -> Player or None:
        """
        Connect checks
        """

        usr_voice = itr.user.voice
        if not usr_voice:  # author not in voice channel
            await itr.response.send_message(
                lang["music"]["voice_client"]["error"]["user_no_voice"]
            )
            return "error"
        vcl = itr.guild.voice_client
        if vcl:
            if vcl.channel is usr_voice.channel and cnt_cmd:
                await itr.response.send_message(
                    lang["music"]["voice_client"]["error"]["already_connected"]
                )
        return vcl

    async def _connect(self, itr: Interaction, lang: dict, cnt_cmd: bool = False) -> Player:
        """
        Initialize a player and connect to a voice channel if there are none.
        """

        player = await self.connect_check(itr, lang, cnt_cmd)
        if player == "error":
            return
        elif player is None:
            if cnt_cmd:
                await itr.response.send_message(
                    lang["music"]["voice_client"]["status"]["connecting"]
                )
            player = await itr.user.voice.channel.connect(
                self_deaf=True,
                cls=Player
            )
            if cnt_cmd:
                await itr.edit_original_response(
                    content=lang["music"]["voice_client"]["status"]["connected"]
                )
        return player

    async def disconnect_check(self, itr: Interaction, lang: dict) -> None or True:
        """
        Disconnect checks
        """

        if not itr.user.voice:  # author not in voice channel
            await itr.response.send_message(
                lang["music"]["voice_client"]["error"]["user_no_voice"]
            )
        if not itr.guild.voice_client:  # bot didn't even connect lol
            await itr.response.send_message(
                lang["music"]["voice_client"]["error"]["not_connected"]
            )
        if itr.guild.voice_client.channel != itr.user.voice.channel:
            await itr.response.send_message(
                lang["music"]["voice_client"]["error"]["playing_in_another_channel"]
            )
        return True

    async def _disconnect(self, itr: Interaction, lang: dict) -> None or True:
        if not self.disconnect_check(itr, lang):
            return
        await itr.response.send_message(
            lang["music"]["voice_client"]["status"]["disconnecting"]
        )
        await itr.guild.voice_client.disconnect()
        await itr.edit_original_response(
            content=lang["music"]["voice_client"]["status"]["disconnected"]
        )
        return True

    @app_commands.checks.cooldown(1, 1.5, key=user_cooldown_check)
    @app_commands.command(name="connect")
    async def connect(self, itr: Interaction):
        """
        Connect to a voice channel.
        """

        lang = await return_user_lang(self, itr.user.id)

        await self._connect(itr, lang, True)
        return

    @app_commands.checks.cooldown(1, 1.5, key=user_cooldown_check)
    @app_commands.command(name="disconnect")
    async def disconnect(self, itr: Interaction):
        """
        Disconnect from a voice channel.
        """

        lang = await return_user_lang(self, itr.user.id)

        await self._disconnect(itr, lang)
        return

    @app_commands.checks.cooldown(1, 1.25, key=user_cooldown_check)
    @app_commands.command(name="play")
    async def play(self, itr: Interaction, query: str):
        """
        Play a song.
        """

        lang = await return_user_lang(self, itr.user.id)

        player: Player = await self._connect(itr, lang)
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["searching"]
        )

        try:
            track: YouTubeTrack = await YouTubeTrack.search(query=query, return_first=True)
            playlist = False
        except AttributeError:
            playlist: YouTubePlaylist = await YouTubePlaylist.search(query=query)

        if playlist:
            for track in playlist.tracks:
                await player.queue.put_wait(track)
                if not player.is_playing():
                    await player.play(await player.queue.get_wait())
            await itr.edit_original_response(content="", embed=rich_embeds(
                NewPlaylist(playlist, lang, query),
                itr.user,
                lang["main"]
            ))
            return

        await player.queue.put_wait(track)
        if not player.is_playing():
            await player.play(await player.queue.get_wait())
        await itr.edit_original_response(content="", embed=rich_embeds(
            NewTrack(track, lang),
            itr.user,
            lang["main"]
        ))

    @app_commands.checks.cooldown(1, 1.75, key=user_cooldown_check)
    @app_commands.command(name="search")
    async def search(self, itr: Interaction, query: str):
        """
        Search for a song.
        """

        lang = await return_user_lang(self, itr.user.id)

        player: Player = await self._connect(itr, lang)
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["searching"]
        )

        tracks: List[Track] = await YouTubeTrack.search(query=query)
        tracks = tracks[:5]
        embed = Embed(
            title=lang["music"]["misc"]["result"],
            description="",
            color=0x00ff00
        )
        counter = 1

        select_menu = MusicSel(tracks, player, lang)
        view = View(timeout=30)

        for track in tracks:
            if counter == 6:
                break
            if len(track.title) > 50:
                title = track.title[:50] + "..."
            else:
                title = track.title

            embed.description += f"{counter}. [{track.title}]({track.uri})\n"
            select_menu.add_option(label=f"{counter}. {title}", value=counter)
            counter += 1

        view.add_item(select_menu)

        await itr.edit_original_response(
            content=lang["music"]["misc"]["result"],
            embed=embed,
            view=view
        )

        if await view.wait():
            view.children[0].disabled = True
            return await itr.edit_original_response(view=view)

    @app_commands.checks.cooldown(1, 1.25, key=user_cooldown_check)
    @app_commands.command(name="pause")
    async def pause(self, itr: Interaction):
        """
        Pause a song.
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        await vcl.pause()
        return await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["paused"]
        )

    @app_commands.checks.cooldown(1, 1.25, key=user_cooldown_check)
    @app_commands.command(name="resume")
    async def resume(self, itr: Interaction):
        """
        Resume a song.
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        await vcl.resume()
        return await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["resumed"]
        )

    @app_commands.checks.cooldown(1, 1.5, key=user_cooldown_check)
    @app_commands.command(name="skip")
    async def skip(self, itr: Interaction):
        """
        Skip a song
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        await vcl.stop()
        await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["skipped"]
        )
        return

    @app_commands.checks.cooldown(1, 2, key=user_cooldown_check)
    @app_commands.command(name="stop")
    async def stop(self, itr: Interaction):
        """
        Stop playing music.
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        if not vcl.queue.is_empty:
            vcl.queue.clear()
        await vcl.stop()
        await itr.response.send_message(
            lang["music"]["misc"]["action"]["music"]["stopped"]
        )

    @app_commands.checks.cooldown(1, 1.5, key=user_cooldown_check)
    @app_commands.command(name="queue")
    async def queue(self, itr: Interaction):
        """
        Show the queue.
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        if vcl.queue.is_empty:
            return await itr.response.send_message(
                lang["music"]["misc"]["action"]["error"]["no_queue"]
            )

        queue_embeds = make_queue(vcl.queue, lang)
        if len(queue_embeds) > 1:
            select_menu = PageSel(
                len(queue_embeds),
                queue_embeds,
                lang,
                itr
            )
            for i in range(len(queue_embeds)):
                select_menu.add_option(label=i + 1, value=i + 1)
            view = View(timeout=60).add_item(select_menu)
        else:
            view = None

        await itr.response.send_message(
            embed=rich_embeds(
                queue_embeds[0],
                itr.user,
                lang["main"]
            ),
            view=view if view is not None else None
        )

        if await view.wait():
            view.children[0].disabled = True
            await itr.edit_original_response(view=view)

    @app_commands.checks.cooldown(1, 1.25, key=user_cooldown_check)
    @app_commands.command(name="nowplaying")
    async def nowplaying(self, itr: Interaction):
        """
        Show the now playing song.
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        if not vcl.is_playing():
            return await itr.response.send_message(
                lang["music"]["misc"]["action"]["error"]["no_music"]
            )

        track: YouTubeTrack = vcl.track
        embed = rich_embeds(
            Embed(
                title=lang["music"]["misc"]["now_playing"],
                description=f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(vcl.position)}/{seconds_to_time(track.duration)}",
            ),
            itr.user,
            lang["main"]
        )
        return await itr.response.send_message(embed=embed)

    @app_commands.checks.cooldown(1, 1.75, key=user_cooldown_check)
    @app_commands.command(name="clear_queue")
    async def clear_queue(self, itr: Interaction):
        """
        Clear the queue
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        if vcl.queue.is_empty:
            return await itr.response.send_message(
                lang["music"]["misc"]["action"]["error"]["no_queue"]
            )

        vcl.queue.clear()
        await itr.response.send_message(
            lang["music"]["misc"]["action"]["queue"]["cleared"]
        )

    @app_commands.checks.cooldown(1, 1.25, key=user_cooldown_check)
    @app_commands.command(name="loop")
    async def loop(self, itr: Interaction, mode: Literal["off", "queue", "song"]):
        """
        Loop queue, song or turn loop off
        """

        lang = await return_user_lang(self, itr.user.id)

        vcl: Player = await self._connect(itr, lang)
        if mode == "song":
            vcl.queue.put_at_front(vcl.track)
        elif mode == "off" and vcl.loop_mode == "song":
            await vcl.queue.get_wait()
        vcl.loop_mode = mode if mode != "off" else None

        await itr.response.send_message(
            lang["music"]["misc"]["action"]["loop"][mode]
        )
