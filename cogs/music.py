"""
This is the music cog.
"""

from logging import Logger
from typing import Literal

from discord import Embed, Interaction, Member, WebhookMessage
from discord.app_commands import checks, command, guild_only
from discord.ext.commands import Cog, GroupCog
from wavelink import (
    Node, NodeReadyEventPayload, Playlist, Pool, QueueMode,
    TrackEndEventPayload, TrackExceptionEventPayload, TrackStartEventPayload,
    WebsocketClosedEventPayload
)

from akatsuki_du_ca import AkatsukiDuCa
from config import config
from models.music_embeds import (
    NewPlaylistEmbed, NewTrackEmbed, QueuePaginator, make_queue_embed
)
from models.music_player import Player
from modules import wavelink_helpers
from modules.lang import get_lang
from modules.log import logger
from modules.misc import (
    GuildTextableChannel, rich_embed, seconds_to_time, user_cooldown_check
)
from modules.wavelink_helpers import get_lang_and_player, search


class RadioMusic(GroupCog, name = "radio"):
    """
    Radio commands for bot
    """

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        logger.info("Radio cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Radio cog unloaded")
        return await super().cog_unload()

    @checks.cooldown(1, 10, key = user_cooldown_check)
    @command(name = "suggest")
    async def suggest(self, interaction: Interaction, song: str):
        """
        Got new songs for my radio? Thank you so much ♥
        """

        suggests_channel = self.bot.get_channel(957341782721585223)
        if not isinstance(suggests_channel, GuildTextableChannel):
            return

        await suggests_channel.send(
            f"{interaction.user} suggested {song} \n" +
            f"User ID: {interaction.user.id}, Guild ID: {interaction.guild_id}"
        )

        lang = await get_lang(interaction.user.id)

        await interaction.response.send_message(lang("music.suggestion_sent"))


class MusicCog(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    bot: AkatsukiDuCa

    def __init__(self, bot: AkatsukiDuCa) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        logger.info("Music cog loaded")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        logger.info("Music cog unloaded")
        return await super().cog_unload()

    @staticmethod
    async def connect_nodes(bot: AkatsukiDuCa):
        """
        Connect to Lavalink nodes.
        """

        await Pool.connect(
            client = bot,
            nodes = [
                Node(uri = node.uri, password = node.password)
                for node in config.lavalink_nodes
            ],
        )

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: NodeReadyEventPayload):
        """
        Event fired when a node has finished connecting.
        """
        logger.info(f"Connected to {payload.node.uri}")

    @Cog.listener()
    async def on_wavelink_websocket_closed(
        self, payload: WebsocketClosedEventPayload
    ):
        """
        Event fired when the Node websocket has been closed by Lavalink.
        """

        if not payload.player: return

        logger.info(f"Disconnected from {payload.player.node.uri}")
        logger.info(f"Reason: {payload.reason} | Code: {payload.code}")

    @Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEndEventPayload):
        """
        Event fired when a track ends.
        """

        player = payload.player
        assert isinstance(player, Player)

        if player.queue.mode == QueueMode.loop:
            player.queue.put_at(0, payload.track)
        if player.queue.mode == QueueMode.loop_all:
            await player.queue.put_wait(payload.track)

        if len(player.queue) == 0:
            if player.end_behavior == "disconnect":
                player.dj, player.text_channel = None, None
                return await player.disconnect()

        await player.play(await player.queue.get_wait())

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackStartEventPayload):
        """
        Event fired when a track starts.
        """

        track = payload.track
        player = payload.player
        assert isinstance(player, Player)

        assert player.dj
        lang = await get_lang(player.dj.id)

        embed = NewTrackEmbed(track, lang)
        embed.title = lang("music.misc.now_playing")

        assert player.text_channel
        await player.text_channel.send(
            embed = rich_embed(embed, player.dj, lang)
        )

    @Cog.listener()
    async def on_wavelink_track_exception(
        self, payload: TrackExceptionEventPayload
    ):
        logger.error(f"Track exception: {payload.exception.get('message')}")

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "connect")
    @guild_only()
    async def connect(self, interaction: Interaction):
        """
        Connect to a voice channel.
        """

        return await wavelink_helpers.connect(
            interaction,
            await get_lang(interaction.user.id),
            force_connect = True
        )

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "disconnect")
    @guild_only()
    async def disconnect(self, interaction: Interaction):
        """
        Disconnect from a voice channel.
        """

        return await wavelink_helpers.disconnect(
            interaction, await get_lang(interaction.user.id)
        )

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "play")
    @guild_only()
    async def play(self, interaction: Interaction, query: str | None = None):
        """
        Play a song.
        """

        lang, player = await get_lang_and_player(
            interaction, should_connect = True
        )
        if not query:
            if not player.paused:
                return await interaction.edit_original_response(
                    content = lang("music.misc.action.error.no_music")
                )
            await player.pause(False)
            return await interaction.edit_original_response(
                content = lang("music.misc.action.music.resumed")
            )

        assert isinstance(interaction.channel, GuildTextableChannel)
        assert isinstance(interaction.user, Member)
        player.dj, player.text_channel = interaction.user, interaction.channel
        await interaction.edit_original_response(
            content = lang("music.misc.action.music.searching")
        )

        result = await search(query)
        if not result:
            return await interaction.edit_original_response(
                content = lang("music.voice_client.error.not_found")
            )

        await player.queue.put_wait(result, atomic = False)

        embed: Embed
        if isinstance(result, Playlist):
            embed = NewPlaylistEmbed(result, lang)
        else:
            embed = NewTrackEmbed(result, lang)

        await interaction.edit_original_response(
            content = "",
            embed = rich_embed(embed, interaction.user, lang),
        )

        if not player.playing and not player.current:
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "playtop")
    @guild_only()
    async def playtop(self, interaction: Interaction, query: str):
        """
        Play or add a song on top of the queue
        """

        lang, player = await get_lang_and_player(
            interaction, should_connect = True
        )

        assert isinstance(interaction.channel, GuildTextableChannel)
        assert isinstance(interaction.user, Member)
        player.dj, player.text_channel = interaction.user, interaction.channel
        await interaction.edit_original_response(
            content = lang("music.misc.action.music.searching")
        )

        result = await search(query)
        if not result:
            return await interaction.edit_original_response(
                content = lang("music.voice_client.error.not_found")
            )

        player.queue.put_at(0, result)

        embed: Embed
        if isinstance(result, Playlist):
            embed = NewPlaylistEmbed(result, lang)
        else:
            embed = NewTrackEmbed(result, lang)

        await interaction.edit_original_response(
            content = "",
            embed = rich_embed(embed, interaction.user, lang),
        )

        if not player.playing and not player.current:
            await player.play(await player.queue.get_wait())

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "pause")
    @guild_only()
    async def pause(self, interaction: Interaction):
        """
        Pause a song.
        """

        lang, player = await get_lang_and_player(interaction)
        if not player or not player.current:
            await interaction.response.send_message(
                content = lang("music.misc.action.error.no_music")
            )
            return

        await player.pause(True)
        return await interaction.response.send_message(
            content = lang("music.misc.action.music.paused")
        )

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "skip")
    @guild_only()
    async def skip(self, interaction: Interaction):
        """
        Skip a song
        """

        lang, player = await get_lang_and_player(interaction)
        if not player.current:
            return await interaction.response.send_message(
                content = lang("music.misc.action.error.no_music")
            )

        await player.stop()
        return await interaction.response.send_message(
            content = lang("music.misc.action.music.skipped")
        )

    @checks.cooldown(1, 2, key = user_cooldown_check)
    @command(name = "stop")
    @guild_only()
    async def stop(self, interaction: Interaction):
        """
        Stop playing music.
        """

        lang, player = await get_lang_and_player(interaction)
        if not len(player.queue) == 0:
            player.queue.clear()
        await player.stop()
        return await interaction.response.send_message(
            content = lang("music.misc.action.music.stopped")
        )

    @checks.cooldown(1, 1.5, key = user_cooldown_check)
    @command(name = "queue")
    @guild_only()
    async def queue(self, interaction: Interaction):
        """
        Show the queue.
        """

        lang, player = await get_lang_and_player(interaction)
        if len(player.queue) == 0:
            return await interaction.response.send_message(
                content = lang("music.misc.action.error.no_queue")
            )

        await interaction.response.defer()

        generator = make_queue_embed(player.queue, lang)

        first_embed = next(generator)
        if not first_embed:
            return await interaction.followup.send(
                content = lang("music.misc.action.error.no_queue")
            )

        message: WebhookMessage = await interaction.followup.send(
            embed = rich_embed(first_embed[0], interaction.user, lang),
        )

        second_embed = next(generator)

        if second_embed:
            view = QueuePaginator([first_embed[0], second_embed[0]],
                                  interaction, lang, generator)
            await message.edit(view = view)
            await view.wait()
            view.disable()
            await message.edit(view = view)

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "nowplaying")
    @guild_only()
    async def nowplaying(self, interaction: Interaction):
        """
        Show the now playing song.
        """

        lang, player = await get_lang_and_player(
            interaction, should_playing = True
        )

        track = player.current
        embed = rich_embed(
            Embed(
                title = lang("music.misc.now_playing"),
                description =
                f"[**{track.title}**]({track.uri}) - {track.author}\n" +
                f"Duration: {seconds_to_time(round(player.position / 1000))}/{seconds_to_time(round(track.length / 1000))}",
            ),
            interaction.user,
            lang,
        )
        return await interaction.response.send_message(
            content = "", embed = embed
        )

    @checks.cooldown(1, 1.75, key = user_cooldown_check)
    @command(name = "clear_queue")
    @guild_only()
    async def clear_queue(self, interaction: Interaction):
        """
        Clear the queue
        """

        lang, player = await get_lang_and_player(interaction)
        if len(player.queue) == 0:
            return await interaction.response.send_message(
                content = lang("music.misc.action.error.no_queue")
            )

        player.queue.clear()
        return await interaction.response.send_message(
            content = lang("music.misc.action.queue.cleared")
        )

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "loop")
    @guild_only()
    async def loop_music(
        self,
        interaction: Interaction,
        mode: Literal["off", "song", "queue"] | None = None,
    ):
        """
        Loop queue, song or turn loop off
        """

        lang, player = await get_lang_and_player(interaction)
        if not player.playing:
            await interaction.response.send_message(
                content = lang("music.misc.action.error.no_music")
            )
            return

        if mode:
            if mode == "off":
                player.queue.mode = QueueMode.normal
            if mode == "song":
                player.queue.mode = QueueMode.loop
            if mode == "queue":
                player.queue.mode = QueueMode.loop_all

        mode = "off" if player.queue.mode == QueueMode.normal else "queue" if player.queue.mode == QueueMode.loop_all else "song"

        await interaction.response.send_message(
            content = lang("music.misc.action.loop")[mode]
        )

    @checks.cooldown(1, 1.25, key = user_cooldown_check)
    @command(name = "seek")
    @guild_only()
    async def seek(self, interaction: Interaction, position: int):
        """
        Seeks to a certain point in the current track.
        """

        lang, player = await get_lang_and_player(interaction)
        if not player.playing:
            await interaction.response.send_message(
                content = lang("music.misc.action.error.no_music")
            )
            return

        position *= 1000

        if player.current.length < position:
            # lmao seek over track
            return await interaction.response.send_message(
                content = "Lmao how to seek over track"
            )

        await player.seek(position)
        return await interaction.response.send_message(content = "\U0001f44c")

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "volume")
    @guild_only()
    async def volume(
        self, interaction: Interaction, volume: int | None = None
    ):
        """
        Change the player volume.
        """

        lang, player = await get_lang_and_player(
            interaction, should_playing = True
        )

        if volume is None:
            return await interaction.response.send_message(
                content = lang("music.misc.volume.current") % player.volume
            )

        await player.set_volume(volume)
        return await interaction.response.send_message(
            content = lang("music.misc.volume.changed") % volume
        )

    @checks.cooldown(1, 1, key = user_cooldown_check)
    @command(name = "speed")
    @guild_only()
    async def speed(
        self, interaction: Interaction, speed: float | None = None
    ):
        """
        Change the player speed.
        """

        lang, player = await get_lang_and_player(
            interaction, should_playing = True
        )

        filters = player.filters

        if speed is None:
            return await interaction.response.send_message(
                content = lang("music.misc.speed.current") %
                filters.timescale.speed
            )

        filters.timescale.set(speed = speed)
        await player.set_filters(filters)
        return await interaction.response.send_message(
            content = lang("music.misc.speed.changed") % speed
        )

    @checks.cooldown(1, 3, key = user_cooldown_check)
    @command(name = "shuffle")
    @guild_only()
    async def shuffle(self, interaction: Interaction):
        """
        Shuffle the queue
        """

        lang, player = await get_lang_and_player(interaction)
        if len(player.queue) == 0:
            return await interaction.response.send_message(
                content = lang("music.misc.action.error.no_queue")
            )

        player.queue.shuffle()
        return await interaction.response.send_message(
            content = lang("music.misc.action.queue.shuffled")
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
    #     if len(player.queue) == 0:
    #         return await interaction.response.send_message(
    #             lang("music.misc.action.error.no_queue")
    #         )

    #     for _ in range(len(player.queue)):
    #         await player.queue.put_wait(player.queue.get())

    #     return await interaction.response.send_message(
    #         lang("music.misc.action.queue.flipped")
    #     )
