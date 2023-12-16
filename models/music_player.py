from typing import Literal

from discord import Member
from wavelink import Player as WavelinkPlayer

from modules.misc import GuildTextableChannel


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    dj: Member | None = None
    text_channel: GuildTextableChannel | None = None
    loop_mode: Literal["song", "queue", "off"] = "off"
    end_behavior: Literal["disconnect"] | None = "disconnect"
