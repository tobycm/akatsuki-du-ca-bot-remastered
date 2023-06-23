"""
Models and functions for easy use for music cog
"""

from typing import Callable, Literal

from discord import Embed, Interaction, TextChannel, Thread, VoiceChannel
from discord.ui import Select
from wavelink import Playable
from wavelink import Player as WavelinkPlayer
from wavelink import Queue, YouTubePlaylist, YouTubeTrack

from modules.misc import rich_embed, seconds_to_time


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    interaction: Interaction | None = None
    text_channel: TextChannel | Thread | VoiceChannel | None = None
    loop_mode: Literal["song", "queue"] | None = None


class MusicSelect(Select):
    """
    Make a music selection Select
    """

    def __init__(
        self, tracks: list[YouTubeTrack], player: Player, lang: Callable[[str], str]
    ) -> None:
        self.lang = lang
        self.tracks = tracks
        self.player = player

        super().__init__(placeholder="Make your music selection")

    async def callback(self, interaction: Interaction):
        track = self.tracks[int(self.values[0]) - 1]
        await self.player.queue.put_wait(track)
        if not self.player.is_playing():
            await self.player.play(await self.player.queue.get_wait())  # type: ignore
        await interaction.response.send_message(
            embed=rich_embed(
                Embed(
                    title=self.lang("music.misc.action.queue.added"),
                    description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
                    + f"Duration: {seconds_to_time(track.duration / 1000)}",
                ).set_thumbnail(
                    url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
                ),
                interaction.user,
                self.lang,
            )
        )
        return


class PageSelect(Select):
    """
    Make a page selection Select
    class queue_page_select(Select):
    """

    def __init__(
        self, embeds: list[Embed], itr: Interaction, lang: Callable[[str], str]
    ) -> None:
        self.embeds = embeds
        self.interaction = itr
        self.lang = lang

        super().__init__(placeholder="Choose page")

    async def callback(self, interaction: Interaction):
        page = int(self.values[0]) - 1

        await interaction.response.defer()
        await self.interaction.edit_original_response(
            embed=rich_embed(self.embeds[page], interaction.user, self.lang)
        )

        return


class NewTrackEmbed(Embed):
    """
    Make a new track embed
    """

    def __init__(self, track: Playable, lang: Callable[[str], str]) -> None:
        super().__init__(
            title=lang("music.misc.action.queue.added"),
            description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
            + f"Duration: {seconds_to_time(track.duration / 1000)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
        )


class NewPlaylistEmbed(Embed):
    """
    Make a new playlist embed
    """

    def __init__(self, playlist: YouTubePlaylist, lang: Callable[[str], str]) -> None:
        super().__init__(
            title=lang("music.misc.action.queue.added"),
            description=f"[**{playlist.name}**]({playlist.uri})\n"
            + f"Items: {len(playlist.tracks)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
        )


class QueueEmbed(Embed):
    """
    Make a queue page embed
    """

    def __init__(self, lang: Callable[[str], str]) -> None:
        super().__init__(title=lang("music.misc.queue"), description="")


def make_queue(queue: Queue, lang: Callable[[str], str]) -> list[Embed]:
    """
    Make queue pages embeds
    """
    embeds = []
    embed = QueueEmbed(lang)
    counter = 1

    for track in queue:
        if len(embed) > 1024:
            embeds.append(embed)
            embed = QueueEmbed(lang)
        if len(embeds) == 5:
            break
        embed.description += f"{counter}. {track.title}\n"  # type: ignore
        counter += 1

    if len(embeds) == 0:
        embeds.append(embed)

    return embeds
