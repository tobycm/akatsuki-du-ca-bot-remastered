from discord import Embed, Interaction, app_commands
from discord.ext.commands import Cog

class ToysCog(Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        
    