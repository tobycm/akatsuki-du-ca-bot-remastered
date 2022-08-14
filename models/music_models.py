"""
Models and functions for easy use for music cog
"""

from typing import List
from discord import Embed, Interaction, TextChannel, Thread
from discord.ui import Select
from wavelink import Track, Player, YouTubePlaylist, WaitQueue

from modules.checks_and_utils import seconds_to_time
from modules.embed_process import rich_embeds

class MusicSel(Select):
    """
    Make a music selection Select
    """

    def __init__(self, tracks : List[Track], player : Player, lang : dict) -> None:
        self.tracks : List[Track] = tracks
        self.player : Player = player
        self.lang : dict = lang
        
        super().__init__(placeholder = "Make your music selection")

    async def callback(self, itr : Interaction):
        track = self.tracks[int(self.values[0]) - 1]
        await self.player.queue.put_wait(track)
        if not self.player.is_playing():
            await self.player.play(await self.player.queue.get_wait())
        await itr.response.send_message(embed = rich_embeds(
            Embed(
                title = self.lang["music"]["misc"]["action"]["queue"]["added"],
                description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"),
            itr.user,
            self.lang["main"]
        ))
        return
    
class PageSel(Select):
    """
    Make a page selection Select
    class queue_page_select(Select):
    """
    
    def __init__(self, embed_size : int, embeds : List[Embed], lang : dict, itr : Interaction) -> None:
        self.embed_size : int = embed_size
        self.embeds : List[Embed] = embeds
        self.lang : dict = lang
        self.itr : Interaction = itr
        
        super().__init__(placeholder = "Choose page")

    async def callback(self, itr : Interaction):
        page = int(self.values[0]) - 1
        
        await itr.response.defer()
        await self.itr.edit_original_message(
            embed = rich_embeds(
                self.embeds[page],
                itr.user,
                self.lang["main"]
            )
        )
        
        return
    
    
class NewTrack(Embed):
    """
    Make a new track embed
    """

    def __init__(self, track : Track, lang : dict) -> None:
        super().__init__(
            title = lang["music"]["misc"]["action"]["queue"]["added"],
            description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
        )
        self.set_thumbnail(
            url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
        )
        
class NewPlaylist(Embed):
    """
    Make a new playlist embed
    """

    def __init__(self, playlist : YouTubePlaylist, lang : dict, url : str) -> None:
        super().__init__(
            title = lang["music"]["misc"]["action"]["queue"]["added"],
            description = f"[**{playlist.name}**]({url})\nItems: {len(playlist.tracks)}",
        )
        self.set_thumbnail(
            url = f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
        )
        
class QueueEmb(Embed):
    """
    Make a queue page embed
    """
    def __init__(self, lang : dict) -> None:
        super().__init__(
            title = lang["music"]["misc"]["queue"],
            description = ""
        )
        
def make_queue(queue : WaitQueue, lang : dict) -> List[Embed]:
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

class Player(Player):
    text_channel : TextChannel or Thread
    loop_mode : str or None