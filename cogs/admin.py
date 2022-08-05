from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import GroupCog, Cog, Context, Bot

from modules.checks_and_utils import check_owners, guild_cooldown_check
from modules.database_utils import delete_prefix, set_prefix
from modules.vault import get_channel_config

class PrefixCog(GroupCog, name = "prefix"):
    def __init__(self, bot : Bot):
        self.bot = bot
        super().__init__()
        
    @app_commands.checks.cooldown(1, 1, key = guild_cooldown_check)
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.command(name = "set")
    async def setprefix(self, interaction : Interaction, prefix : str):
        """
        Set the bot's prefix
        """
        
        author = interaction.user        
        result = await set_prefix(self.bot.redis_ins, author.guild.id, prefix)
        
        if result:
            return await interaction.response.send_message(f"Prefix set to `{prefix}`")
        
        await interaction.response.send_message("Fail to set prefix")
        
        error_channel = self.bot.get_channel(get_channel_config("error"))
        return await error_channel.send(f"{author} tried to set prefix to `{prefix}` but failed. Error: {result}")
    
    @app_commands.checks.cooldown(1, 1, key = guild_cooldown_check)
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.command(name = "reset")
    async def resetprefix(self, interaction : Interaction):
        """
        Reset the bot's prefix
        """
        
        author = interaction.user        
        result = await delete_prefix(self.bot.redis_ins, author.guild.id)
        
        if result:
            return await interaction.response.send_message("Prefix reseted!")
        
        await interaction.response.send_message("Fail to set prefix")
        
        error_channel = self.bot.get_channel(get_channel_config("error"))
        return await error_channel.send(f"{author} tried to reset prefix but failed. Error: {result}")
    
class BotAdminCog(Cog):
    def __init__(self, bot : Bot):
        self.bot = bot
        
    @commands.command(name = "resetguildprefix")
    async def resetguildprefix(self, ctx : Context, guild_id : int):
        """
        Reset a guild prefix remotely
        """
        
        if not await check_owners(self.bot.redis_ins, ctx):
            raise app_commands.MissingPermissions(["manage_guild"])
        
        
        result = await delete_prefix(self.bot.redis_ins, guild_id)
        
        return await ctx.send(f"Prefix reseted for guild {guild_id}" if result else f"Fail to reset prefix. Error: {result}")
    