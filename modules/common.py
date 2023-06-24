from discord import DMChannel, StageChannel, TextChannel, Thread, VoiceChannel

GuildTextChannel = TextChannel | Thread | VoiceChannel | StageChannel
