"""
This is the music cog.
"""

import logging
from typing import Literal, Optional

from discord import Color, Embed, Interaction, TextChannel
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
from modules.lang import get_lang, get_lang_by_address
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
    async def suggest(self, interaction: Interaction, song: str):
        """
        Got new songs for my radio? Thank you so much ♥
        """

        suggests_channel = self.bot.get_channel(957341782721585223)
        if not isinstance(suggests_channel, TextChannel):
            return

        await suggests_channel.send(
            f"{interaction.user} suggested {song} \n"
            + f"User ID: {interaction.user.id}, Guild ID: {interaction.guild_id}"
        )

        await interaction.response.send_message(
            get_lang_by_address(
                "music.SuggestionSent", await get_lang(interaction.user.id)
            )
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

        await player.play(await player.queue.get_wait())

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
        self, interaction: Interaction, connecting: bool, lang: dict
    ) -> Optional[Literal[True]]:
        """
        Connect checks
        """

        user_voice = interaction.user.voice
        if not user_voice:  # author not in voice channel
            await interaction.response.send_message(
                get_lang_by_address("music.voice_client.error.user_no_voice", lang)
            )
            return
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.channel is user_voice.channel) and connecting:
            await interaction.response.send_message(
                get_lang_by_address("music.voice_client.error.already_connected", lang)
            )
            return
        return True

    async def _connect(
        self, interaction: Interaction, connecting: bool, lang: dict
    ) -> Optional[Player]:
        """
        Initialize a player and connect to a voice channel if there are none.
        """

        ok = await self.connect_check(interaction, connecting, lang)
        if not ok:
            return

        if connecting:
            await interaction.response.send_message(
                get_lang_by_address("music.voice_client.status.connecting", lang)
            )

        player = await interaction.user.voice.channel.connect(
            self_deaf=True, cls=Player
        )
        if connecting:
            await interaction.edit_original_response(
                content=get_lang_by_address("music.voice_client.status.connected", lang)
            )
        return player

    async def disconnect_check(
        self, interaction: Interaction, lang: dict
    ) -> Optional[Literal[True]]:
        """
        Disconnect checks
        """

        if not interaction.user.voice:  # author not in voice channel
            await interaction.response.send_message(
                get_lang_by_address("music.voice_client.error.user_no_voice", lang)
            )
            return None
        if not interaction.guild.voice_client:  # bot didn't even connect lol
            await interaction.response.send_message(
                get_lang_by_address("music.voice_client.error.not_connected", lang)
            )
            return None
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message(
                get_lang_by_address(
                    "music.voice_client.error.playing_in_another_channel", lang
                )
            )
        return True

    async def _disconnect(
        self, interaction: Interaction, lang: dict
    ) -> Optional[Literal[True]]:
        if not await self.disconnect_check(interaction, lang):
            return None
        await interaction.response.send_message(
            get_lang_by_address("music.voice_client.status.disconnecting", lang)
        )

        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.edit_original_response(
            content=get_lang_by_address("music.voice_client.status.disconnected", lang)
        )
        return True

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="connect")
    async def connect(self, interaction: Interaction):
        """
        Connect to a voice channel.
        """

        return await self._connect(
            interaction, True, await get_lang(interaction.user.id)
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="disconnect")
    async def disconnect(self, interaction: Interaction):
        """
        Disconnect from a voice channel.
        """

        return await self._disconnect(interaction, await get_lang(interaction.user.id))

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="play")
    async def play(self, interaction: Interaction, query: str):
        """
        Play a song.
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        player.text_channel = interaction.channel
        await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.searching", lang)
        )

        track = await YouTubeTrack.search(query)
        if isinstance(track, list[YouTubeTrack]):
            track = track[0]

        await player.queue.put_wait(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await interaction.edit_original_response(
            content="",
            embed=rich_embeds(
                NewTrackEmbed(track, interaction.user.id), interaction.user
            ),
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="playlist")
    async def playlist(self, interaction: Interaction, query: str):
        """
        Play a list of song.
        """

        player: Player = await self._connect(interaction)
        if not player:
            return
        player.text_channel = interaction.channel
        await interaction.response.send_message(
            get_lang_by_address(
                "music.misc.action.music.searching",
                await get_user_lang(interaction.user.id),
            )
        )

        playlist = await YouTubePlaylist.search(query)
        if isinstance(playlist, list[YouTubePlaylist]):
            playlist = playlist[0]

        for track in playlist.tracks:
            await player.queue.put_wait(track)

        await interaction.edit_original_response(
            content="",
            embed=rich_embeds(
                NewPlaylistEmbed(playlist, query, interaction.user.id), interaction.user
            ),
        )

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="playtop")
    async def playtop(self, interaction: Interaction, query: str):
        """
        Play or add a song on top of the queue
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        player.text_channel = interaction.channel
        await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.searching", lang)
        )

        track = await YouTubeTrack.search(query)
        if isinstance(track, list[YouTubeTrack]):
            track = track[0]

        player.queue.put_at_front(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await interaction.edit_original_response(
            content="",
            embed=rich_embeds(
                NewTrackEmbed(track, interaction.user.id), interaction.user
            ),
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="soundcloud")
    async def soundcloud(self, interaction: Interaction, query: str):
        """
        Search and play a Soundcloud song
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        player.text_channel = interaction.channel
        await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.searching", lang)
        )

        track = await SoundCloudTrack.search(query, return_first=True)

        await player.queue.put_wait(track)

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

        await interaction.edit_original_response(
            content="",
            embed=rich_embeds(
                NewTrackEmbed(track, interaction.user.id), interaction.user, lang
            ),
        )

    @checks.cooldown(1, 1.75, key=user_cooldown_check)
    @command(name="search")
    async def search(self, interaction: Interaction, query: str):
        """
        Search for a song.
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction)
        if not player:
            return
        player.text_channel = interaction.channel
        await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.searching", lang)
        )

        tracks = (await YouTubeTrack.search(query))[:5]

        embed = Embed(
            title=get_lang_by_address("music.misc.result", lang),
            description="",
            color=0x00FF00,
        )
        counter = 1

        select_menu = MusicSelect(tracks, player, interaction.user.id)
        view = View(timeout=30)

        for track in tracks:
            title = track.title if len(track.title) < 50 else track.title[:50] + "..."
            embed.description += f"{counter}. [{track.title}]({track.uri})\n"
            select_menu.add_option(label=f"{counter}. {title}", value=counter)
            counter += 1

        view.add_item(select_menu)

        await interaction.edit_original_response(
            content=get_lang_by_address("music.misc.result", lang),
            embed=embed,
            view=view,
        )

        if await view.wait():
            view.children[0].disabled = True
            return await interaction.edit_original_response(view=view)

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="pause")
    async def pause(self, interaction: Interaction):
        """
        Pause a song.
        """

        lang = await get_lang(interaction.user.id)

        await (await self._connect(interaction, lang)).pause()
        return await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.paused", lang)
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="resume")
    async def resume(self, interaction: Interaction):
        """
        Resume a song.
        """

        lang = await get_lang(interaction.user.id)

        await (await self._connect(interaction, lang)).resume()
        return await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.resumed", lang)
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="skip")
    async def skip(self, interaction: Interaction):
        """
        Skip a song
        """

        lang = await get_lang(interaction.user.id)

        await (await self._connect(interaction, lang)).stop()
        return await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.skipped", lang)
        )

    @checks.cooldown(1, 2, key=user_cooldown_check)
    @command(name="stop")
    async def stop(self, interaction: Interaction):
        """
        Stop playing music.
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        if not player.queue.is_empty:
            player.queue.clear()
        await player.stop()
        return await interaction.response.send_message(
            get_lang_by_address("music.misc.action.music.stopped", lang)
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="queue")
    async def queue(self, interaction: Interaction):
        """
        Show the queue.
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        if player.queue.is_empty:
            return await interaction.response.send_message(
                get_lang_by_address("music.misc.action.error.no_queue", lang)
            )

        queue_embeds = make_queue(player.queue, interaction.user.id, lang)

        view = None
        if len(queue_embeds) > 1:
            select_menu = PageSelect(queue_embeds, interaction, lang)
            for i in range(len(queue_embeds)):
                select_menu.add_option(label=i + 1, value=i + 1)
            view = View(timeout=60).add_item(select_menu)

        await interaction.response.send_message(
            embed=rich_embeds(queue_embeds[0], interaction.user, lang),
            view=view,
        )

        if await view.wait():
            view.children[0].disabled = True
            await interaction.edit_original_response(view=view)

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="nowplaying")
    async def nowplaying(self, interaction: Interaction):
        """
        Show the now playing song.
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        if not player.is_playing():
            return await interaction.response.send_message(
                get_lang_by_address("music.misc.action.error.no_music", lang)
            )

        track: YouTubeTrack = player.track
        embed = rich_embeds(
            Embed(
                title=get_lang_by_address("music.misc.now_playing", lang),
                description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
                + f"Duration: {seconds_to_time(player.position)}/{seconds_to_time(track.duration)}",
            ),
            interaction.user,
            lang,
        )
        return await interaction.response.send_message(embed=embed)

    @checks.cooldown(1, 1.75, key=user_cooldown_check)
    @command(name="clear_queue")
    async def clear_queue(self, interaction: Interaction):
        """
        Clear the queue
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        if player.queue.is_empty:
            return await interaction.response.send_message(
                get_lang_by_address("music.misc.action.error.no_queue", lang)
            )

        player.queue.clear()
        return await interaction.response.send_message(
            get_lang_by_address("music.misc.action.queue.cleared", lang)
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="loop")
    async def loop_music(
        self, interaction: Interaction, mode: Literal["off", "queue", "song"]
    ):
        """
        Loop queue, song or turn loop off
        """

        lang = await get_lang(interaction.user.id)

        player: Player = await self._connect(interaction, lang)
        if not player:
            return
        if mode == "song":
            player.queue.put_at_front(player.current)
        if mode == "off" and player.loop_mode == "song":
            await player.queue.get_wait()
        player.loop_mode = mode if mode != "off" else None

        await interaction.response.send_message(
            get_lang_by_address("music.misc.action.loop", lang)[mode]
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="seek")
    async def seek(self, interaction: Interaction, position: int):
        """
        Seeks to a certain point in the current track.
        """

        player: Player = await self._connect(
            interaction, await get_lang(interaction.user.id)
        )
        if not player:
            return
        if player.current.length < position:
            # lmao seek over track
            return await interaction.response.send_message(
                "Lmao how to seek over track"
            )

        await player.seek(position=position)
        return await interaction.response.send_message("Done!")
