from typing import Literal

from discord import GuildTextableChannel, Member
from wavelink import Player as WavelinkPlayer


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    dj: Member | None = None
    text_channel: GuildTextableChannel | None = None
    loop_mode: Literal["song", "queue", "off"] = "off"
