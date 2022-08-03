from typing import List
from discord import Embed, Interaction
from discord.ui import Select
from wavelink import Track, Player

from modules.checks_and_utils import seconds_to_time
from modules.embed_process import rich_embeds

class music_select(Select):
    def __init__(self, tracks : List[Track], player : Player, lang : dict) -> None:
        self.tracks : List[Track] = tracks
        self.player : Player = player
        self.lang : dict = lang
        
        super().__init__(placeholder = "Make your music selection")

    async def callback(self, interaction : Interaction):
        track = self.tracks[int(self.values[0]) - 1]
        await self.player.queue.put_wait(track)
        if not self.player.is_playing():
            await self.player.play(await self.player.queue.get_wait())
        await interaction.response.send_message(embed = rich_embeds(
            Embed(
                title = self.lang["music"]["misc"]["action"]["queue"]["added"],
                description = f"[**{track.title}**]({track.uri}) - {track.author}\nDuration: {seconds_to_time(track.duration)}",
            ).set_thumbnail(url = f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"),
            interaction.user,
            self.lang["main"]
        ))
        return