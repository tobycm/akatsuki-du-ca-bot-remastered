"""
Models and functions for easy use for music cog
"""

from typing import List
from discord import CategoryChannel, Embed, Interaction
from discord.ui import Select
from wavelink import Track, Player as WavelinkPlayer, YouTubePlaylist, WaitQueue

from modules.checks_and_utils import seconds_to_time
from modules.embed_process import rich_embeds

class Player(WavelinkPlayer):
    """
    Custom player class
    """

    text_channel: CategoryChannel
    loop_mode: str or None

class MusicSel(Select):
    """
    Make a music selection Select
    """

    def __init__(self, tracks: List[Track], player: Player, lang: dict) -> None:
        self.tracks: List[Track] = tracks
        self.player: Player = player
        self.lang: dict = lang

        super().__init__(placeholder="Make your music selection")

    async def callback(self, interaction: Interaction):
        track = self.tracks[int(self.values[0]) - 1]
        await self.player.queue.put_wait(track)
        if not self.player.is_playing():
            await self.player.play(await self.player.queue.get_wait())
        await interaction.response.send_message(embed=rich_embeds(
            Embed(
                title=self.lang["music"]["misc"]["action"]["queue"]["added"],
                description=f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            ).set_thumbnail(url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"),
            interaction.user,
            self.lang["main"]
        ))
        return


class PageSel(Select):
    """
    Make a page selection Select
    class queue_page_select(Select):
    """

    def __init__(self, embed_size: int, embeds: List[Embed], lang: dict, itr: Interaction) -> None:
        self.embed_size: int = embed_size
        self.embeds: List[Embed] = embeds
        self.lang: dict = lang
        self.itr: Interaction = itr

        super().__init__(placeholder="Choose page")

    async def callback(self, interaction: Interaction):
        page = int(self.values[0]) - 1

        await interaction.response.defer()
        await self.itr.edit_original_response(
            embed=rich_embeds(
                self.embeds[page],
                interaction.user,
                self.lang["main"]
            )
        )

        return


class NewTrack(Embed):
    """
    Make a new track embed
    """

    def __init__(self, track: Track, lang: dict) -> None:
        super().__init__(
            title=lang["music"]["misc"]["action"]["queue"]["added"],
            description=f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
        )


class NewPlaylist(Embed):
    """
    Make a new playlist embed
    """

    def __init__(self, playlist: YouTubePlaylist, lang: dict, url: str) -> None:
        super().__init__(
            title=lang["music"]["misc"]["action"]["queue"]["added"],
            description=f"[**{playlist.name}**]({url})\nItems: {len(playlist.tracks)}",
        )
        self.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
        )


class QueueEmb(Embed):
    """
    Make a queue page embed
    """

    def __init__(self, lang: dict) -> None:
        super().__init__(
            title=lang["music"]["misc"]["queue"],
            description=""
        )


def make_queue(queue: WaitQueue, lang: dict) -> List[Embed]:
    """
    Make queue pages embeds
    """
    embeds = []
    embed = QueueEmb(lang)
    counter = 1

    for track in queue:
        if len(embed) > 1024:
            embeds.append(embed)
            embed = QueueEmb(lang)
        if len(embeds) == 5:
            break
        embed.description += f"{counter}. {track.title}\n"
        counter += 1

    if len(embeds) == 0:
        embeds.append(embed)

    return embeds


