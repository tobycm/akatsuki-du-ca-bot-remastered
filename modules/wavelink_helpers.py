from discord import Interaction, Member
from wavelink import (
    SoundCloudPlaylist, SoundCloudTrack, YouTubeMusicTrack, YouTubePlaylist,
    YouTubeTrack
)
from wavelink.ext.spotify import SpotifyTrack
from yarl import URL

from models.music_player import Player
from modules.lang import Lang, get_lang


async def check_youtube(
    url: URL, query: str
) -> YouTubeTrack or YouTubePlaylist or None:

    if url.host not in (
        "youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"
    ):
        return None

    playlist_id = url.query.get("list")
    video_id = url.query.get("v")
    if video_id:
        return await YouTubeTrack.search(video_id)
    if playlist_id and url.path == "/playlist":
        return await YouTubePlaylist.search(playlist_id)
    return await YouTubeTrack.search(query)


async def check_soundcloud(
    url: URL
) -> SoundCloudTrack or SoundCloudPlaylist or None:
    if url.host not in (
        "soundcloud.com", "on.soundcloud.com", "m.soundcloud.com"
    ):
        return None
    if "sets" in url.parts:
        return await SoundCloudPlaylist.search(
            "/".join(part for part in url.parts if part != "sets")
        )
    return await SoundCloudTrack.search(url.path)


async def search(
    query: str
) -> YouTubeTrack | YouTubeMusicTrack | SoundCloudTrack | SpotifyTrack | YouTubePlaylist | SoundCloudPlaylist | None:
    """
    Search for a song or playlist
    """

    url = URL(query)

    result = []

    try:
        if url.host == "music.youtube.com":
            result = await YouTubeMusicTrack.search(query)
        if url.host == "open.spotify.com":
            result = await SpotifyTrack.search(query)

        result = result or await check_soundcloud(url) or await check_youtube(
            url, query
        ) or await YouTubeTrack.search(query)

    except:
        return None

    if not result:
        return None

    if isinstance(result, list):
        result = result[0]
    if isinstance(result, (YouTubePlaylist, SoundCloudPlaylist)):
        return result
    if isinstance(
        result,
        (YouTubeTrack, SoundCloudTrack, SpotifyTrack, YouTubeMusicTrack)
    ):
        return result

    return None


async def connect_check(
    interaction: Interaction,
    lang: Lang,
    connecting: bool = False,
) -> bool:
    """
    Connect checks
    """

    assert isinstance(interaction.user, Member)
    assert interaction.guild

    user_voice = interaction.user.voice
    if not user_voice: # author not in voice channel
        await interaction.response.send_message(
            lang("music.voice_client.error.user_no_voice")
        )
        return False
    voice_client = interaction.guild.voice_client
    if not voice_client and not connecting: return True
    if voice_client.channel is user_voice.channel:
        await interaction.response.send_message(
            lang("music.voice_client.error.already_connected")
        )
        return False
    return True


async def connect(
    interaction: Interaction,
    lang: Lang,
    connecting: bool = False,
) -> Player | None: # aka get player
    """
    Initialize a player and connect to a voice channel if there are none.
    """

    if not await connect_check(interaction, lang, connecting = connecting):
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
        interaction.guild.voice_client or await
        interaction.user.voice.channel.connect(self_deaf = True, cls = Player)
    )

    assert isinstance(player, Player)

    if connecting:
        await interaction.edit_original_response(
            content = lang("music.voice_client.status.connected")
        )
    return player


async def disconnect_check(interaction: Interaction, lang: Lang) -> bool:
    """
    Disconnect checks
    """

    assert interaction.guild
    assert isinstance(interaction.user, Member)

    if not interaction.user.voice: # author not in voice channel
        await interaction.response.send_message(
            lang("music.voice_client.error.user_no_voice")
        )
        return False
    if not interaction.guild.voice_client: # bot didn't even connect lol
        await interaction.response.send_message(
            lang("music.voice_client.error.not_connected")
        )
        return False
    if interaction.guild.voice_client.channel != interaction.user.voice.channel:
        await interaction.response.send_message(
            lang("music.voice_client.error.playing_in_another_channel")
        )
    return True


async def disconnect(interaction: Interaction, lang: Lang) -> bool:
    assert interaction.guild
    assert interaction.guild.voice_client

    if not await disconnect_check(interaction, lang):
        return False
    await interaction.response.send_message(
        lang("music.voice_client.status.disconnecting")
    )

    await interaction.guild.voice_client.disconnect(force = True)
    await interaction.edit_original_response(
        content = lang("music.voice_client.status.disconnected")
    )
    return True


async def get_lang_and_player(interaction: Interaction) -> tuple[Lang, Player]:
    """
    Get lang and player
    """

    assert interaction.guild
    assert interaction.user

    lang = await get_lang(interaction.user.id)
    player = await connect(interaction, lang)
    if not player:
        raise Exception("Failed to connect to voice channel")
    return lang, player
