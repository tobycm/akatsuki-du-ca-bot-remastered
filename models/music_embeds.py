import copy
from typing import Generator, cast

import validators
from discord import ButtonStyle, Embed, Interaction
from discord.ui import Button, View, button
from wavelink import Playable, Playlist, Queue

from modules.lang import Lang
from modules.misc import rich_embed, seconds_to_time


class NewTrackEmbed(Embed):
    """
    Make a new track embed
    """

    def __init__(
        self,
        track: Playable,
        lang: Lang,
    ) -> None:
        title = (
            f"**{track.title}**"
            if not hasattr(track, "uri") or not validators.url(track.uri) else
            f"[**{track.title}**]({track.uri})"
        )

        super().__init__(
            title = lang("music.misc.action.queue.added"),
            description =
            f"{title} - {track.author if not track.artist.url else f'[{track.author}]({track.artist.url})'}\n"
            + f"Duration: {seconds_to_time(round(track.length / 1000))}",
        )

        if track.artwork:
            self.set_thumbnail(url = track.artwork)

        if track.source == "youtube":
            self.set_thumbnail(
                url = track.artwork or
                f"https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg"
            )


class NewPlaylistEmbed(Embed):
    """
    Make a new playlist embed
    """

    def __init__(self, playlist: Playlist, lang: Lang) -> None:
        super().__init__(
            title = lang("music.misc.action.queue.added"),
            description = f"**{playlist.name}**\n" + f"Items: {len(playlist)}",
        )

        if playlist.artwork:
            self.set_thumbnail(url = playlist.artwork)
            return
        try:
            self.set_thumbnail(
                url =
                f"https://i.ytimg.com/vi/{playlist.tracks[0].identifier}/maxresdefault.jpg"
            )
        except:
            pass


class QueueEmbed(Embed):
    """
    Make a queue page embed
    """

    description: str

    def __init__(self, lang: Lang) -> None:
        super().__init__(title = lang("music.misc.queue"), description = "")


class QueuePaginator(View):
    embeds: list[QueueEmbed]
    page: int
    original_interaction: Interaction
    lang: Lang
    embed_generator: Generator[tuple[QueueEmbed, int] | None, None, None]

    def __init__(
        self,
        embeds_init: list[QueueEmbed],
        interaction: Interaction,
        lang: Lang,
        embed_generator: Generator[tuple[QueueEmbed, int] | None, None, None],
    ):
        self.page = 0
        self.embeds = embeds_init
        self.original_interaction = interaction
        self.lang = lang
        self.embed_generator = embed_generator

        super().__init__(timeout = 60)

    def disable(self):
        for child in self.children:
            cast(Button, child).disabled = True

    @button(label = "◀", style = ButtonStyle.blurple)
    async def previous(self, interaction: Interaction, _: Button):
        self.page -= 1
        if self.page < 0:
            self.page = 0
            return await interaction.response.send_message(
                content = "No more pages"
            )

        embed = self.embeds[self.page]
        await interaction.response.send_message(content = "Changed page")
        await self.original_interaction.response.edit_message(
            embed = rich_embed(embed, interaction.user, self.lang)
        )

    @button(label = "▶", style = ButtonStyle.blurple)
    async def next(self, interaction: Interaction, _: Button):
        self.page += 1
        if len(self.embeds) < self.page: # make embed
            try:
                new_embed = next(self.embed_generator)
            except StopIteration:
                self.page -= 1
                return await interaction.response.send_message(
                    content = "No more pages"
                )

            self.embeds.append(new_embed[0])
            self.page = new_embed[1]

        embed = self.embeds[self.page]

        await interaction.response.send_message(content = "Changed page")
        await self.original_interaction.response.edit_message(
            embed = rich_embed(embed, interaction.user, self.lang)
        )


def make_queue_embed(queue: Queue, lang: Lang): # embed, page number
    """
    Make queue pages embeds
    """

    page = 0

    original_embed = QueueEmbed(lang)

    index = 0

    while index < len(queue):
        track = queue[index]
        embed = copy.deepcopy(original_embed)

        while len(embed.description
                  ) + len(f"{index + 1}. {track.title}\n") < 4000:
            embed.description += f"{index + 1}. {track.title}\n"
            index += 1

        embed.set_footer(text = f"Page {page + 1}")
        embed.set_author(name = f"Queue - {len(queue)} items")

        page += 1
        yield embed, page
