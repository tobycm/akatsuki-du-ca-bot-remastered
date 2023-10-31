from wavelink import (
    SoundCloudPlaylist, SoundCloudTrack, YouTubePlaylist, YouTubeTrack
)
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
