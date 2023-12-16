from modules.vault import (
    API, Bot, ChannelsConfig, Config, HomeGuild, LavalinkNode, Redis, Spotify,
    OsuAPI, TenorAPI
)

config = Config(
    bot = Bot(
        token = "",
        secret = "",
        prefix = "",
        home_guild = HomeGuild(id = 0, invite = ""),
        channels = ChannelsConfig(error = 0, bug = 0)
    ),
    api = API(
        osu = OsuAPI(key = ""),
        tenor = TenorAPI(key = ""),
        spotify = Spotify(client_id = "", client_secret = "")
    ),
    lavalink_nodes = [LavalinkNode(uri = "", password = "")],
    redis = Redis(
        host = "", port = 0, username = "", password = "", database = 0
    )
)
