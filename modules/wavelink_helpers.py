from typing import Awaitable, Callable, Literal, TypeAlias

from discord import Interaction, Member
from wavelink import Playable, Playlist

from models.music_player import Player
from modules.exceptions import MusicException
from modules.lang import Lang, get_lang
from modules.log import logger

VoiceCheck: TypeAlias = Callable[[Interaction], Awaitable[None]]


class VoiceChecks:

    @staticmethod
    def __get_player(interaction: Interaction) -> Player:
        """
        Get player
        
        Should be used only when bot is connected
        """

        assert interaction.guild
        assert isinstance(interaction.guild.voice_client, Player)
        return interaction.guild.voice_client

    @staticmethod
    async def has_current(interaction: Interaction) -> None:
        """
        Check if bot has a track playing
        """

        if VoiceChecks.__get_player(interaction).current:
            return

        raise MusicException.NotPlaying

    @staticmethod
    async def playing(interaction: Interaction) -> None:
        """
        Check if bot is actually playing a track
        """

        if VoiceChecks.__get_player(interaction).playing:
            return

        raise MusicException.NotPlaying

    @staticmethod
    async def has_queue(interaction: Interaction) -> None:
        """
        Check if bot has a queue
        """

        if len(VoiceChecks.__get_player(interaction).queue) > 0:
            return

        raise MusicException.QueueEmpty

    # no use because can make /play request url to add track
    # also missing lang
    # @staticmethod
    # async def paused(interaction: Interaction, lang: Lang) -> bool:
    #     """
    #     Check if bot is paused
    #     """

    #     player = VoiceChecks.__get_player(interaction)

    #     if player.paused:
    #         return True

    #     await interaction.edit_original_response(
    #         content = lang("music.voice_client.error.not_paused")
    #     )
    #     return False


async def search(query: str) -> Playable | Playlist | None:
    """
    Search for a song or playlist
    """

    try:
        result = await Playable.search(query)
    except Exception as error:
        logger.debug(f"Error while searching for track: {error}")
        return None

    logger.debug(f"Track searching result: {result}")

    if not result:
        return None

    if isinstance(result, list):
        return result[0]
    if isinstance(result, Playlist):
        return result

    return None


async def connect_check(
    interaction: Interaction,
    new_connection: bool = False,
) -> None:
    """
    Connect checks
    """

    assert interaction.guild
    assert isinstance(interaction.user, Member)

    if not interaction.user.voice: # author not in voice channel
        raise MusicException.AuthorNotInVoice

    if not interaction.guild.voice_client: return # ok to connect

    if new_connection:
        raise MusicException.AlreadyConnected

    if interaction.guild.voice_client.channel != interaction.user.voice.channel:
        raise MusicException.DifferentVoice


async def connect(
    interaction: Interaction,
    lang: Lang,
    should_connect: bool = False,
    new_connection: bool = False,
    checks: list[VoiceCheck] = [],
) -> Player: # aka get player
    """
    Initialize a player or connect to a voice channel if there are none.
    """

    await connect_check(interaction, new_connection = new_connection)

    assert interaction.guild

    player = interaction.guild.voice_client

    if player:
        assert isinstance(player, Player)

        for check in checks:
            await check(interaction)

        return player

    if not should_connect:
        raise MusicException.NotConnected

    await interaction.edit_original_response(
        content = lang("music.voice_client.status.connecting")
    )

    assert interaction.guild
    assert isinstance(interaction.user, Member)
    assert interaction.user.voice
    assert interaction.user.voice.channel

    player = await interaction.user.voice.channel.connect(
        self_deaf = True, cls = Player
    )

    await interaction.edit_original_response(
        content = lang("music.voice_client.status.connected")
    )

    return player


async def disconnect_check(interaction: Interaction) -> None:
    """
    Disconnect checks
    """

    assert interaction.guild
    assert isinstance(interaction.user, Member)

    if not interaction.user.voice: # author not in voice channel
        raise MusicException.AuthorNotInVoice

    if not interaction.guild.voice_client: # bot didn't even connect lol
        raise MusicException.NotConnected

    if interaction.guild.voice_client.channel != interaction.user.voice.channel:
        raise MusicException.DifferentVoice


async def disconnect(interaction: Interaction, lang: Lang) -> None:
    await disconnect_check(interaction)
    assert interaction.guild
    assert interaction.guild.voice_client

    await interaction.response.send_message(
        lang("music.voice_client.status.disconnecting")
    )

    await interaction.guild.voice_client.disconnect(force = True)
    await interaction.edit_original_response(
        content = lang("music.voice_client.status.disconnected")
    )


async def get_lang_and_player(
    interaction: Interaction,
    should_connect: bool = False,
    checks: list[VoiceCheck] = [],
) -> tuple[Lang, Player]:
    """
    Get lang and player
    """

    assert interaction.guild
    assert interaction.user

    await interaction.response.send_message("...")

    lang = await get_lang(interaction.user.id)

    return lang, await connect(
        interaction, lang, should_connect = should_connect, checks = checks
    )
