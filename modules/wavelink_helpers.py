from wavelink import (
    SoundCloudPlaylist, SoundCloudTrack, YouTubeMusicTrack, YouTubePlaylist,
    YouTubeTrack
)
from wavelink.ext.spotify import SpotifyTrack
from yarl import URL


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
