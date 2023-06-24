"""
Models and functions for easy use for music cog
"""

from typing import Callable, Literal

from discord import Embed, Interaction
from discord.ui import Select
from wavelink import Playable
from wavelink import Player as WavelinkPlayer
from wavelink import Queue, YouTubePlaylist, YouTubeTrack

from modules.common import GuildTextChannel
from modules.misc import rich_embed, seconds_to_time
