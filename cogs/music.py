"""
This is the music cog.
"""

from typing import Callable, Literal

from discord import Color, Embed, Interaction, Member, TextChannel
from discord.app_commands import checks, command, guild_only
from discord.ext.commands import Cog, GroupCog
from discord.ui import Select, View
from wavelink import Node, NodePool
from wavelink import Player as WavelinkPlayer
from wavelink import (
    Queue,
    SoundCloudPlaylist,
    SoundCloudTrack,
    TrackEventPayload,
    WebsocketClosedPayload,
    YouTubeMusicTrack,
    YouTubePlaylist,
    YouTubeTrack,
)
from wavelink.ext.spotify import SpotifyClient, SpotifyTrack
from yarl import URL

from akatsuki_du_ca import AkatsukiDuCa
from modules.lang import get_lang
from modules.misc import rich_embed, seconds_to_time, user_cooldown_check


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    dj: Member | None = None
    text_channel: TextChannel | None = None
    loop_mode: Literal["song", "queue", "off"] = "off"


class NewTrackEmbed(Embed):
    """
    Make a new track embed
    """

    def __init__(
        self,
        track: YouTubeTrack | YouTubeMusicTrack | SoundCloudTrack | SpotifyTrack,
        lang: Callable[[str], str],
    ) -> None:
        if isinstance(track, SpotifyTrack):
            author = ", ".join(track.artists)
        else:
            author = track.author

        title = (
            f"**{track.title}**"
            if isinstance(track, SpotifyTrack)
            else f"[**{track.title}**]({track.uri})"
        )

        super().__init__(
            title=lang("music.misc.action.queue.added"),
            description=f"{title} - {author}\n"
            + f"Duration: {seconds_to_time(round(track.duration / 1000))}",
        )

        if isinstance(track, SpotifyTrack):
            self.set_thumbnail(url=track.images[0])

        if isinstance(track, (YouTubeTrack, YouTubeMusicTrack)):
            self.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
            )


class NewPlaylistEmbed(Embed):
    """
    Make a new playlist embed
    """

    def __init__(
        self, playlist: YouTubePlaylist | SoundCloudPlaylist, lang: Callable[[str], str]
    ) -> None:
        super().__init__(
            title=lang("music.misc.action.queue.added"),
            description=f"**{playlist.name}**\n" + f"Items: {len(playlist.tracks)}",
        )
        if isinstance(playlist, YouTubePlaylist):
            self.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
            )


class QueueEmbed(Embed):
    """
    Make a queue page embed
    """

    def __init__(self, lang: Callable[[str], str]) -> None:
        super().__init__(title=lang("music.misc.queue"), description="")


class PageSelect(Select):
    """
    Make a page selection Select
    class queue_page_select(Select):
    """

    def __init__(
        self,
        embeds: list[QueueEmbed],
        interaction: Interaction,
        lang: Callable[[str], str],
    ) -> None:
        self.embeds = embeds
        self.interaction = interaction
        self.lang = lang

        super().__init__(placeholder="Choose page")

    async def callback(self, interaction: Interaction):
        page = int(self.values[0]) - 1

        await interaction.response.defer()
        await self.interaction.edit_original_response(
            embed=rich_embed(self.embeds[page], interaction.user, self.lang)
        )

        return


def make_queue(queue: Queue, lang: Callable[[str], str]) -> list[QueueEmbed]:
    """
    Make queue pages embeds
    """
    embeds = []
    embed = QueueEmbed(lang)

    for index, track in enumerate(queue):
        if len(embed) > 1000:
            embeds.append(embed)
            embed = QueueEmbed(lang)
        if len(embeds) == 25:
            break
        embed.description += f"{index}. {track.title}\n"  # type: ignore

    if len(embeds) == 0:
        embeds.append(embed)

    return embeds


class RadioMusic(GroupCog, name="radio"):
    """
    Radio commands for bot
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
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

        lang = await get_lang(interaction.user.id)

        await interaction.response.send_message(lang("music.suggestion_sent"))


class MusicCog(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        self.logger = bot.logger
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

        spotify = SpotifyClient(
            client_id=self.bot.config.spotify.client_id,
            client_secret=self.bot.config.spotify.client_secret,
        )

        await NodePool.connect(
            client=self.bot,
            nodes=[
                Node(uri=node.uri, password=node.password)
                for node in self.bot.config.lavalink_nodes
            ],
            spotify=spotify,
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

        assert isinstance(payload.player, Player)
        player = payload.player
        assert player.text_channel

        await player.text_channel.send(f"{payload.track.title} has ended")
        if player.queue.is_empty:
            player.dj, player.text_channel, player.loop_mode = None, None, "off"
            return await player.disconnect()

        await player.play(await player.queue.get_wait())  # type: ignore

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload):
        """
        Event fired when a track starts.
        """

        track = payload.track
        assert isinstance(
            track, (YouTubeTrack, YouTubeMusicTrack, SpotifyTrack, SoundCloudTrack)
        )
        player = payload.player
        assert isinstance(player, Player)

        assert player.dj
        lang = await get_lang(player.dj.id)

        embed = NewTrackEmbed(track, lang)

        embed.title = lang("music.misc.now_playing")

        if player.loop_mode == "song":
            player.queue.put_at_front(track)
        elif player.loop_mode == "queue":
            await player.queue.put_wait(track)

        assert player.text_channel
        await player.text_channel.send(embed=embed)

    async def connect_check(
        self,
        interaction: Interaction,
        lang: Callable[[str], str],
        connecting: bool = False,
    ) -> Literal[True] | None:
        """
        Connect checks
        """

        assert isinstance(interaction.user, Member)
        assert interaction.guild

        user_voice = interaction.user.voice
        if not user_voice:  # author not in voice channel
            await interaction.response.send_message(
                lang("music.voice_client.error.user_no_voice")
            )
            return None
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.channel is user_voice.channel) and connecting:
            await interaction.response.send_message(
                lang("music.voice_client.error.already_connected")
            )
            return None
        return True

    async def _connect(
        self,
        interaction: Interaction,
        lang: Callable[[str], str],
        connecting: bool = False,
    ) -> Player | None:
        """
        Initialize a player and connect to a voice channel if there are none.
        """

        if not await self.connect_check(interaction, lang, connecting=connecting):
            return None

        if connecting:
            await interaction.response.send_message(
                lang("music.voice_client.status.connecting")
            )

        assert isinstance(interaction.user, Member)
        assert interaction.user.voice
        assert interaction.user.voice.channel
        assert interaction.guild

        player = (
            interaction.guild.voice_client
            or await interaction.user.voice.channel.connect(
                self_deaf=True, cls=Player  # type: ignore
            )
        )

        assert isinstance(player, Player)

        if connecting:
            await interaction.edit_original_response(
                content=lang("music.voice_client.status.connected")  # type: ignore
            )
        return player

    async def disconnect_check(
        self, interaction: Interaction, lang: Callable[[str], str]
    ) -> Literal[True] | None:
        """
        Disconnect checks
        """

        assert interaction.guild
        assert isinstance(interaction.user, Member)

        if not interaction.user.voice:  # author not in voice channel
            await interaction.response.send_message(
                lang("music.voice_client.error.user_no_voice")
            )
            return None
        if not interaction.guild.voice_client:  # bot didn't even connect lol
            await interaction.response.send_message(
                lang("music.voice_client.error.not_connected")
            )
            return None
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            await interaction.response.send_message(
                lang("music.voice_client.error.playing_in_another_channel")
            )
        return True

    async def _disconnect(
        self, interaction: Interaction, lang: Callable[[str], str]
    ) -> Literal[True] | None:
        assert interaction.guild
        assert interaction.guild.voice_client

        if not await self.disconnect_check(interaction, lang):
            return None
        await interaction.response.send_message(
            lang("music.voice_client.status.disconnecting")
        )

        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.edit_original_response(
            content=lang("music.voice_client.status.disconnected")  # type: ignore
        )
        return True

    async def search(
        self, query: str
    ) -> YouTubeTrack | YouTubeMusicTrack | SoundCloudTrack | SpotifyTrack | YouTubePlaylist | SoundCloudPlaylist | None:
        """
        Search for a song or playlist
        """

        url = URL(query)

        result = []

        try:
            if not url.host:
                result = await YouTubeTrack.search(query)
            if (
                url.host == "youtube.com"
                or url.host == "youtu.be"
                or url.host == "m.youtube.com"
            ):
                if url.parts[0] == "playlist":
                    result = await YouTubePlaylist.search(query)
                else:
                    result = await YouTubeTrack.search(query)

            if url.host == "music.youtube.com":
                result = await YouTubeMusicTrack.search(query)

            if (
                url.host == "soundcloud.com"
                or url.host == "on.soundcloud.com"
                or url.host == "m.soundcloud.com"
            ):
                if "sets" in url.parts:
                    result = await SoundCloudPlaylist.search(url.parts[-1])
                else:
                    result = await SoundCloudTrack.search(url.parts[-1])

            if url.host == "open.spotify.com":
                result = await SpotifyTrack.search(query)
        except:
            return None

        if not result:
            return None

        if isinstance(result, list):
            if len(result) == 0:
                return None
            result = result[0]

        if isinstance(result, YouTubePlaylist) or isinstance(
            result, SoundCloudPlaylist
        ):
            return result
        elif (
            isinstance(result, YouTubeTrack)
            or isinstance(result, SoundCloudTrack)
            or isinstance(result, YouTubeMusicTrack)
            or isinstance(result, SpotifyTrack)
        ):
            return result

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="connect")
    @guild_only()
    async def connect(self, interaction: Interaction):
        """
        Connect to a voice channel.
        """

        return await self._connect(
            interaction, await get_lang(interaction.user.id), connecting=True
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="disconnect")
    @guild_only()
    async def disconnect(self, interaction: Interaction):
        """
        Disconnect from a voice channel.
        """

        return await self._disconnect(interaction, await get_lang(interaction.user.id))

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="play")
    @guild_only()
    async def play(self, interaction: Interaction, query: str | None = None):
        """
        Play a song.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return

        if not query:
            if not player.is_paused():
                return await interaction.response.send_message(
                    lang("music.misc.action.error.no_music")
                )
            return await player.resume()

        assert isinstance(interaction.channel, TextChannel)
        assert isinstance(interaction.user, Member)
        player.dj, player.text_channel = interaction.user, interaction.channel
        await interaction.response.send_message(
            lang("music.misc.action.music.searching")
        )

        result = await self.search(query)
        if not result:
            return await interaction.edit_original_response(
                content=lang("music.voice_client.error.not_found")
            )

        await player.queue.put_wait(result)

        if isinstance(result, YouTubePlaylist) or isinstance(
            result, SoundCloudPlaylist
        ):
            embed = NewPlaylistEmbed(result, lang)
        else:
            embed = NewTrackEmbed(result, lang)

        await interaction.edit_original_response(
            content="",
            embed=rich_embed(embed, interaction.user, lang),
        )

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="playtop")
    @guild_only()
    async def playtop(self, interaction: Interaction, query: str):
        """
        Play or add a song on top of the queue
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return

        assert isinstance(interaction.channel, TextChannel)
        assert isinstance(interaction.user, Member)
        player.dj, player.text_channel = interaction.user, interaction.channel
        await interaction.response.send_message(
            lang("music.misc.action.music.searching")
        )

        result = await self.search(query)
        if not result:
            return await interaction.edit_original_response(
                content=lang("music.voice_client.error.not_found")
            )

        player.queue.put_at_front(result)

        if isinstance(result, YouTubePlaylist) or isinstance(
            result, SoundCloudPlaylist
        ):
            embed = NewPlaylistEmbed(result, lang)
        else:
            embed = NewTrackEmbed(result, lang)

        await interaction.edit_original_response(
            content="",
            embed=rich_embed(embed, interaction.user, lang),
        )

        if not player.is_playing():
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="pause")
    @guild_only()
    async def pause(self, interaction: Interaction):
        """
        Pause a song.
        """

        lang = await get_lang(interaction.user.id)
        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        await player.pause()
        return await interaction.response.send_message(
            lang("music.misc.action.music.paused")
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="skip")
    @guild_only()
    async def skip(self, interaction: Interaction):
        """
        Skip a song
        """

        lang = await get_lang(interaction.user.id)
        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        await player.stop()
        return await interaction.response.send_message(
            lang("music.misc.action.music.skipped")
        )

    @checks.cooldown(1, 2, key=user_cooldown_check)
    @command(name="stop")
    @guild_only()
    async def stop(self, interaction: Interaction):
        """
        Stop playing music.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return
        if not player.queue.is_empty:
            player.queue.clear()
        await player.stop()
        return await interaction.response.send_message(
            lang("music.misc.action.music.stopped")
        )

    @checks.cooldown(1, 1.5, key=user_cooldown_check)
    @command(name="queue")
    @guild_only()
    async def queue(self, interaction: Interaction):
        """
        Show the queue.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return
        if player.queue.is_empty:
            return await interaction.response.send_message(
                lang("music.misc.action.error.no_queue")
            )

        queue_embeds = make_queue(player.queue, lang)

        if len(queue_embeds) > 1:
            select_menu = PageSelect(queue_embeds, interaction, lang)
            for i in range(len(queue_embeds)):
                select_menu.add_option(label=str(i + 1), value=str(i + 1))
            view = View(timeout=60).add_item(select_menu)

            await interaction.response.send_message(
                embed=rich_embed(queue_embeds[0], interaction.user, lang),
                view=view,
            )

            if await view.wait():
                assert isinstance(view.children[0], PageSelect)
                view.children[0].disabled = True
                await interaction.edit_original_response(view=view)
        else:
            await interaction.response.send_message(
                embed=rich_embed(queue_embeds[0], interaction.user, lang),
            )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="nowplaying")
    @guild_only()
    async def nowplaying(self, interaction: Interaction):
        """
        Show the now playing song.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        track = player.current
        embed = rich_embed(
            Embed(
                title=lang("music.misc.now_playing"),
                description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
                + f"Duration: {seconds_to_time(round(player.position / 1000))}/{seconds_to_time(round(track.duration / 1000))}",
            ),
            interaction.user,
            lang,
        )
        return await interaction.response.send_message(embed=embed)

    @checks.cooldown(1, 1.75, key=user_cooldown_check)
    @command(name="clear_queue")
    @guild_only()
    async def clear_queue(self, interaction: Interaction):
        """
        Clear the queue
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return
        if player.queue.is_empty:
            return await interaction.response.send_message(
                lang("music.misc.action.error.no_queue")
            )

        player.queue.clear()
        return await interaction.response.send_message(
            lang("music.misc.action.queue.cleared")
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="loop")
    @guild_only()
    async def loop_music(
        self,
        interaction: Interaction,
        mode: Literal["off", "queue", "song"] | None = None,
    ):
        """
        Loop queue, song or turn loop off
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        if mode:
            player.loop_mode = mode
        if mode == "song":
            player.queue.put_at_front(player.current)
        if mode == "off" and player.loop_mode == "song":
            await player.queue.get_wait()

        await interaction.response.send_message(
            lang("music.misc.action.loop")[player.loop_mode or "off"]  # type: ignore
        )

    @checks.cooldown(1, 1.25, key=user_cooldown_check)
    @command(name="seek")
    @guild_only()
    async def seek(self, interaction: Interaction, position: int):
        """
        Seeks to a certain point in the current track.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        if player.current.length < position:
            # lmao seek over track
            return await interaction.response.send_message(
                "Lmao how to seek over track"
            )

        await player.seek(position=position)
        return await interaction.response.send_message("Done!")

    @checks.cooldown(1, 1, key=user_cooldown_check)
    @command(name="volume")
    @guild_only()
    async def volume(self, interaction: Interaction, volume: int | None = None):
        """
        Change the player volume.
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player or not player.is_playing() or not player.current:
            await interaction.response.send_message(
                lang("music.misc.action.error.no_music")
            )
            return

        if volume is None:
            return await interaction.response.send_message(
                lang("music.misc.volume.current") % f"{player.volume}%"
            )

        await player.set_volume(volume)
        return await interaction.response.send_message(
            lang("music.misc.volume.changed") % f"{volume}%"
        )

    @checks.cooldown(1, 3, key=user_cooldown_check)
    @command(name="shuffle")
    @guild_only()
    async def shuffle(self, interaction: Interaction):
        """
        Shuffle the queue
        """

        lang = await get_lang(interaction.user.id)

        player = await self._connect(interaction, lang)
        if not player:
            return
        if player.queue.is_empty:
            return await interaction.response.send_message(
                lang("music.misc.action.error.no_queue")
            )

        player.queue.shuffle()
        return await interaction.response.send_message(
            lang("music.misc.action.queue.shuffled")
        )

    # @checks.cooldown(1, 3, key=user_cooldown_check)
    # @command(name="flip")
    # async def flip(self, interaction: Interaction):
    #     """
    #     Flip the queue
    #     """

    #     lang = await get_lang(interaction.user.id)

    #     player = await self._connect(interaction, lang)
    #     if not player:
    #         return
    #     if player.queue.is_empty:
    #         return await interaction.response.send_message(
    #             lang("music.misc.action.error.no_queue")
    #         )

    #     for _ in range(len(player.queue)):
    #         await player.queue.put_wait(player.queue.get())

    #     return await interaction.response.send_message(
    #         lang("music.misc.action.queue.flipped")
    #     )
