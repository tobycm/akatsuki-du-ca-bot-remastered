from typing import Literal

from discord import Member
from wavelink import Player as WavelinkPlayer

from modules.misc import GuildTextableChannelType


class Player(WavelinkPlayer):
    """
    Custom player class
    """

    dj: Member | None = None
    text_channel: GuildTextableChannelType | None = None
    end_behavior: Literal["disconnect"] | None = "disconnect"
