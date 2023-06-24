from discord import DMChannel, StageChannel, TextChannel, Thread, VoiceChannel

GuildTextBasedChannel = TextChannel | Thread | VoiceChannel | StageChannel
TextBasedChannel = GuildTextBasedChannel | DMChannel
