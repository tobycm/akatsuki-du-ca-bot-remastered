from discord import app_commands, Interaction
from discord.ext.commands import GroupCog

from modules.checks_and_utils import guild_cooldown_check
from modules.database_utils import delete_prefix, set_prefix
from modules.log_utils import command_log

class PrefixCog(GroupCog, name = "prefix"):
    def __init__(self, bot):
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
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        
        result = await set_prefix(self.bot.redis_ins, author.guild.id, prefix)
        
        if result:
            return await interaction.response.send_message(f"Prefix set to `{prefix}`")
        
        await interaction.response.send_message("Fail to set prefix")
        
        error_channel = self.bot.get_channel(912563176447561796)
        return await error_channel.send(f"{author} tried to set prefix to `{prefix}` but failed. Error: {result}")
    
    @app_commands.checks.cooldown(1, 1, key = guild_cooldown_check)
    @app_commands.checks.has_permissions(manage_guild = True)
    @app_commands.command(name = "reset")
    async def resetprefix(self, interaction : Interaction):
        """
        Reset the bot's prefix
        """
        
        author = interaction.user
        command_log(author.id, author.guild.id, interaction.channel.id, interaction.command.name)
        
        result = await delete_prefix(self.bot.redis_ins, author.guild.id)
        
        if result:
            return await interaction.response.send_message("Prefix reseted!")
        
        await interaction.response.send_message("Fail to set prefix")
        
        error_channel = self.bot.get_channel(912563176447561796)
        return await error_channel.send(f"{author} tried to reset prefix but failed. Error: {result}")
    
    