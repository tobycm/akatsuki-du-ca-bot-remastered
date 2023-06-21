"""
This is the music cog.
"""

import logging
from typing import Literal, Optional

from discord import Color, Embed, Interaction, TextChannel, VoiceProtocol
from discord.app_commands import checks, command
from discord.ext.commands import Cog, GroupCog
from discord.ui import View
from wavelink import (
    Node,
    NodePool,
    SoundCloudTrack,
    TrackEventPayload,
    WebsocketClosedPayload,
    YouTubePlaylist,
    YouTubeTrack,
)

from models.bot_models import AkatsukiDuCa
from models.music_models import (
    MusicSelect,
    NewPlaylistEmbed,
    NewTrackEmbed,
    PageSelect,
    Player,
    make_queue,
)
from modules.checks_and_utils import seconds_to_time, user_cooldown_check
from modules.database_utils import get_user_lang
from modules.embed_process import rich_embeds
from modules.lang import lang
from modules.vault import get_lavalink_nodes


class RadioMusic(GroupCog, name="radio"):
    """
    Radio commands for bot
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger: logging.Logger = bot.logger
        super().__init__()

    async def cog_load(self) -> None:
        self.logger.info("Radio cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Radio cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 10, key=user_cooldown_check)
    @command(name="suggest")
    async def suggest(self, itr: Interaction, song: str):
        """
        Got new songs for my radio? Thank you so much ♥
        """

        suggests_channel = self.bot.get_channel(957341782721585223)
        if not isinstance(suggests_channel, TextChannel):
            return

        await suggests_channel.send(
            f"{itr.user} suggested {song} \n"
            + f"User ID: {itr.user.id}, Guild ID: {itr.guild_id}"
        )

        await itr.response.send_message(
            lang("music.SuggestionSent", await get_user_lang(itr.user.id))
        )


class MusicCog(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    bot: AkatsukiDuCa
    logger: logging.Logger

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger: logging.Logger = bot.logger
        bot.loop.create_task(self.connect_nodes())

    async def cog_load(self) -> None:
        self.logger.info("Music cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info("Music cog unloaded")
        return await super().cog_unload()

    async def connect_nodes(self):
        """
        Connect to Lavalink nodes.
        """
        await self.bot.wait_until_ready()

        await NodePool.connect(
            client=self.bot,
            nodes=[
                Node(uri=node["uri"], password=node["password"])
                for node in get_lavalink_nodes()
            ],
        )

    @Cog.listener()
    async def on_wavelink_node_ready(self, node: Node):
        """
        Event fired when a node has finished connecting.
        """
        self.logger.info(f"Connected to {node.uri}")

    @Cog.listener()
    async def on_wavelink_websocket_closed(self, payload: WebsocketClosedPayload):
        """
        Event fired when the Node websocket has been closed by Lavalink.
        """

        self.logger.info(f"Disconnected from {payload.player.current_node.uri}")
        self.logger.info(f"Reason: {payload.reason} | Code: {payload.code}")

    @Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload):
        """
        Event fired when a track ends.
        """

        player: Player = payload.player

        await player.text_channel.send(f"{payload.track.title} has ended")
        if player.queue.is_empty:
            player.text_channel, player.loop_mode = None, None
            return await player.disconnect()
        next_track = await player.queue.get_wait()
        await player.play(next_track)

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload):
        """
        Event fired when a track starts.
        """

        track = payload.track
        player: Player = payload.player

        embed = Embed(
            title="Now playing",
            description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
            + f"Duration: {seconds_to_time(track.duration)}",
            color=Color.random(),
        ).set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
        )
        try:
            if player.loop_mode == "song":
                player.queue.put_at_front(track)
            elif player.loop_mode == "queue":
                await player.queue.put_wait(track)
        except AttributeError:
            pass
        await player.text_channel.send(embed=embed)

    async def connect_check(
        self, itr: Interaction, connecting: bool
    ) -> Optional[Literal[True]]:
        """
        Connect checks
        """

        user_voice = itr.user.voice
        if not user_voice:  # author not in voice channel
            await itr.response.send_message(
                lang(
                    "music.voice_client.error.user_no_voice",
                    await get_user_lang(itr.user.id),
                )
            )
            return
        voice_client = itr.guild.voice_client
        if voice_client and (voice_client.channel is user_voice.channel) and connecting:
            await itr.response.send_message(
                lang(
                    "music.voice_client.error.already_connected",
                    await get_user_lang(itr.user.id),
                )
            )
            return
        return True

    async def _connect(
        self, itr: Interaction, connecting: bool = False
    ) -> Optional[Player]:
        """
        Initialize a player and connect to a voice channel if there are none.
        """

        ok = await self.connect_check(itr, connecting)
        if not ok:
            return

        if connecting:
            await itr.response.send_message(
                lang(
                    "music.voice_client.status.connecting",
                    await get_user_lang(itr.user.id),
                )
            )

        player = await itr.user.voice.channel.connect(self_deaf=True, cls=Player)
        if connecting:
            await itr.edit_original_response(
                content=lang(
                    "music.voice_client.status.connected",
                    await get_user_lang(itr.user.id),
                )
            )
        return player

    async def disconnect_check(self, itr: Interaction) -> Optional[Literal[True]]:
        """
        Disconnect checks
        """

        if not itr.user.voice:  # author not in voice channel
            await itr.response.send_message(
                lang(
                    "music.voice_client.error.user_no_voice",
                    await get_user_lang(itr.user.id),
                )
            )
            return None
        if not itr.guild.voice_client:  # bot didn't even connect lol
            await itr.response.send_message(
                lang(
                    "music.voice_client.error.not_connected",
                    await get_user_lang(itr.user.id),
                )
            )
            return None
        if itr.guild.voice_client.channel != itr.user.voice.channel:
            await itr.response.send_message(
                lang(
                    "music.voice_client.error.playing_in_another_channel",
                    await get_user_lang(itr.user.id),
                )
            )
        return True

    async def _disconnect(self, itr: Interaction) -> Optional[Literal[True]]:
        if not await self.disconnect_check(itr):
            return None
        await itr.response.send_message(
            lang(
                "music.voice_client.status.disconnecting",
                await get_user_lang(itr.user.id),
            )
        )

        await itr.guild.voice_client.disconnect(force=True)
        await itr.edit_original_response(
            content=lang(
                "music.voice_client.status.disconnected",
                await get_user_lang(itr.user.id),
            )
        )
        return True

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="connect")
    async def connect(self, itr: Interaction):
        """
        Connect to a voice channel.
        """

        return await self._connect(itr, True)

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="disconnect")
    async def disconnect(self, itr: Interaction):
        """
        Disconnect from a voice channel.
        """

        return await self._disconnect(itr)

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="play")
    async def play(self, itr: Interaction, query: str):
        """
        Play a song.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang("music.misc.action.music.searching", await get_user_lang(itr.user.id))
        )

        track = await YouTubeTrack.search(query)
        if isinstance(track, list[YouTubeTrack]):
            track = track[0]

        await player.queue.put_wait(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await itr.edit_original_response(
            content="",
            embed=rich_embeds(NewTrackEmbed(track, itr.user.id), itr.user),
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="playlist")
    async def playlist(self, itr: Interaction, query: str):
        """
        Play a list of song.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang("music.misc.action.music.searching", await get_user_lang(itr.user.id))
        )

        playlist = await YouTubePlaylist.search(query)
        if isinstance(playlist, list[YouTubePlaylist]):
            playlist = playlist[0]

        for track in playlist.tracks:
            await player.queue.put_wait(track)

        await itr.edit_original_response(
            content="",
            embed=rich_embeds(NewPlaylistEmbed(playlist, query, itr.user.id), itr.user),
        )

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="playtop")
    async def playtop(self, itr: Interaction, query: str):
        """
        Play or add a song on top of the queue
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang("music.misc.action.music.searching", await get_user_lang(itr.user.id))
        )

        track = await YouTubeTrack.search(query)
        if isinstance(track, list[YouTubeTrack]):
            track = track[0]

        player.queue.put_at_front(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await itr.edit_original_response(
            content="",
            embed=rich_embeds(NewTrackEmbed(track, itr.user.id), itr.user),
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="soundcloud")
    async def soundcloud(self, itr: Interaction, query: str):
        """
        Search and play a Soundcloud song
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang("music.misc.action.music.searching", await get_user_lang(itr.user.id))
        )

        track = await SoundCloudTrack.search(query, return_first=True)

        await player.queue.put_wait(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await itr.edit_original_response(
            content="",
            embed=rich_embeds(NewTrackEmbed(track, itr.user.id), itr.user),
        )

    @checks.cooldown(1, 1.75, key=user_cooldown_check)
    @command(name="search")
    async def search(self, itr: Interaction, query: str):
        """
        Search for a song.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        player.text_channel = itr.channel
        await itr.response.send_message(
            lang("music.misc.action.music.searching", await get_user_lang(itr.user.id))
        )

        tracks = (await YouTubeTrack.search(query))[:5]

        embed = Embed(
            title=lang("music.misc.result", await get_user_lang(itr.user.id)),
            description="",
            color=0x00FF00,
        )
        counter = 1

        select_menu = MusicSelect(tracks, player, itr.user.id)
        view = View(timeout=30)

        for track in tracks:
            title = track.title if len(track.title) < 50 else track.title[:50] + "..."
            embed.description += f"{counter}. [{track.title}]({track.uri})\n"
            select_menu.add_option(label=f"{counter}. {title}", value=counter)
            counter += 1

        view.add_item(select_menu)

        await itr.edit_original_response(
            content=lang("music.misc.result", await get_user_lang(itr.user.id)),
            embed=embed,
            view=view,
        )

        if await view.wait():
            view.children[0].disabled = True
            return await itr.edit_original_response(view=view)

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="pause")
    async def pause(self, itr: Interaction):
        """
        Pause a song.
        """

        await (await self._connect(itr)).pause()
        return await itr.response.send_message(
            lang("music.misc.action.music.paused", await get_user_lang(itr.user.id))
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="resume")
    async def resume(self, itr: Interaction):
        """
        Resume a song.
        """

        await (await self._connect(itr)).resume()
        return await itr.response.send_message(
            lang("music.misc.action.music.resumed", await get_user_lang(itr.user.id))
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="skip")
    async def skip(self, itr: Interaction):
        """
        Skip a song
        """

        await (await self._connect(itr)).stop()
        return await itr.response.send_message(
            lang("music.misc.action.music.skipped", await get_user_lang(itr.user.id))
        )

    @checks.cooldown(1, 2, key=user_cooldown_check)
    @command(name="stop")
    async def stop(self, itr: Interaction):
        """
        Stop playing music.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if not player.queue.is_empty:
            player.queue.clear()
        await player.stop()
        return await itr.response.send_message(
            lang("music.misc.action.music.stopped", await get_user_lang(itr.user.id))
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="queue")
    async def queue(self, itr: Interaction):
        """
        Show the queue.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if player.queue.is_empty:
            return await itr.response.send_message(
                lang(
                    "music.misc.action.error.no_queue", await get_user_lang(itr.user.id)
                )
            )

        queue_embeds = make_queue(player.queue, itr.user.id)

        view = None
        if len(queue_embeds) > 1:
            select_menu = PageSelect(queue_embeds, itr)
            for i in range(len(queue_embeds)):
                select_menu.add_option(label=i + 1, value=i + 1)
            view = View(timeout=60).add_item(select_menu)

        await itr.response.send_message(
            embed=rich_embeds(queue_embeds[0], itr.user),
            view=view,
        )

        if await view.wait():
            view.children[0].disabled = True
            await itr.edit_original_response(view=view)

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="nowplaying")
    async def nowplaying(self, itr: Interaction):
        """
        Show the now playing song.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if not player.is_playing():
            return await itr.response.send_message(
                lang(
                    "music.misc.action.error.no_music", await get_user_lang(itr.user.id)
                )
            )

        track: YouTubeTrack = player.track
        embed = rich_embeds(
            Embed(
                title=lang("music.misc.now_playing", await get_user_lang(itr.user.id)),
                description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
                + f"Duration: {seconds_to_time(player.position)}/{seconds_to_time(track.duration)}",
            ),
            itr.user,
        )
        return await itr.response.send_message(embed=embed)

    @checks.cooldown(1, 1.75, key=user_cooldown_check)
    @command(name="clear_queue")
    async def clear_queue(self, itr: Interaction):
        """
        Clear the queue
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if player.queue.is_empty:
            return await itr.response.send_message(
                lang(
                    "music.misc.action.error.no_queue", await get_user_lang(itr.user.id)
                )
            )

        player.queue.clear()
        return await itr.response.send_message(
            lang("music.misc.action.queue.cleared", await get_user_lang(itr.user.id))
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="loop")
    async def loop_music(self, itr: Interaction, mode: Literal["off", "queue", "song"]):
        """
        Loop queue, song or turn loop off
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if mode == "song":
            player.queue.put_at_front(player.current)
        if mode == "off" and player.loop_mode == "song":
            await player.queue.get_wait()
        player.loop_mode = mode if mode != "off" else None

        await itr.response.send_message(
            lang("music.misc.action.loop", await get_user_lang(itr.user.id))[mode]
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="seek")
    async def seek(self, itr: Interaction, position: int):
        """
        Seeks to a certain point in the current track.
        """

        player: Player = await self._connect(itr)
        if not player:
            return
        if player.current.length < position:
            # lmao seek over track
            return await itr.response.send_message("Lmao how to seek over track")

        await player.seek(position=position)
        return await itr.response.send_message("Done!")
