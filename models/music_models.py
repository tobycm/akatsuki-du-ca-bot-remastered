"""
Models and functions for easy use for music cog
"""

from typing import Literal, Optional, Union

from discord import Embed, Interaction, TextChannel
from discord.ui import Select
from wavelink import Player as WavelinkPlayer
from wavelink import Queue, YouTubePlaylist, YouTubeTrack

from modules.checks_and_utils import seconds_to_time
from modules.database_utils import get_user_lang
from modules.embed_process import rich_embeds
from modules.lang import get_lang_with_address


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    text_channel: Optional[TextChannel] = None
    loop_mode: Optional[Union[Literal["song"], Literal["queue"]]] = None


class MusicSelect(Select):
    """
    Make a music selection Select
    """

    def __init__(
        self, tracks: list[YouTubeTrack], player: Player, user_id: int
    ) -> None:
        self.user_id: int = user_id
        self.tracks: list[YouTubeTrack] = tracks
        self.player: Player = player

        super().__init__(placeholder="Make your music selection")

    async def callback(self, interaction: Interaction):
        track = self.tracks[int(self.values[0]) - 1]
        await self.player.queue.put_wait(track)
        if not self.player.is_playing():
            await self.player.play(await self.player.queue.get_wait())
        await interaction.response.send_message(
            embed=rich_embeds(
                Embed(
                    title=get_lang_with_address(
                        "music.misc.action.queue.added", self.user_id
                    ),
                    description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
                    + f"Duration: {seconds_to_time(track.duration)}",
                ).set_thumbnail(
                    url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
                ),
                interaction.user,
                await get_user_lang(interaction.user.id)
            )
        )
        return


class PageSelect(Select):
    """
    Make a page selection Select
    class queue_page_select(Select):
    """

    def __init__(self, embeds: list[Embed], interaction: Interaction) -> None:
        self.embeds: list[Embed] = embeds
        self.interaction: Interaction = interaction

        super().__init__(placeholder="Choose page")

    async def callback(self, interaction: Interaction):
        page = int(self.values[0]) - 1

        await interaction.response.defer()
        await self.interaction.edit_original_response(
            embed=rich_embeds(self.embeds[page], interaction.user)
        )

        return


class NewTrackEmbed(Embed):
    """
    Make a new track embed
    """

    def __init__(self, track: YouTubeTrack, user_id: int) -> None:
        super().__init__(
            title=get_lang_with_address("music.misc.action.queue.added", user_id),
            description=f"[**{track.title}**]({track.uri}) - {track.author}\n"
            + f"Duration: {seconds_to_time(track.duration)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
        )


class NewPlaylistEmbed(Embed):
    """
    Make a new playlist embed
    """

    def __init__(self, playlist: YouTubePlaylist, url: str, user_id: int) -> None:
        super().__init__(
            title=get_lang_with_address("music.misc.action.queue.added", user_id),
            description=f"[**{playlist.name}**]({url})\n"
            + f"Items: {len(playlist.tracks)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
        )


class QueueEmbed(Embed):
    """
    Make a queue page embed
    """

    def __init__(self, user_id: int) -> None:
        super().__init__(
            title=get_lang_with_address("music.misc.queue", user_id), description=""
        )


def make_queue(queue: Queue, user_id: int) -> list[Embed]:
    """
    Make queue pages embeds
    """
    embeds = []
    embed = QueueEmbed(user_id)
    counter = 1

    for track in queue:
        if len(embed) > 1024:
            embeds.append(embed)
            embed = QueueEmbed(user_id)
        if len(embeds) == 5:
            break
        embed.description += f"{counter}. {track.title}\n"
        counter += 1

    if len(embeds) == 0:
        embeds.append(embed)

    return embeds
