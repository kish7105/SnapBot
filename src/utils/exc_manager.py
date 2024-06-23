from discord import Interaction, app_commands as app

from utils.errors import NotOwner, NotValidURL
from utils.msg_format import format_as_error_msg


async def exception_manager(interaction: Interaction, error: app.AppCommandError) -> None:
    """A helper function for handling for the most commonly encountered exceptions in command executions.

    Parameters
    ----------
    interaction : `discord.Interaction`
        Represents a Discord Interaction
        
    error : `app.AppCommandError`
        The error that occurred during the command execution
    """
    
    # If the command is on cooldown
    if isinstance(error, app.CommandOnCooldown):
        await interaction.response.send_message(format_as_error_msg(f"Woah.. calm down buddy! Retry after ``{error.retry_after: .2f} seconds``"), ephemeral=True)
        
    # If the bot lacks permissions to execute a command
    elif isinstance(error, app.BotMissingPermissions):
        await interaction.response.send_message(format_as_error_msg("I don't have the necessary permissions to use this command!"), ephemeral=True)
        
    # If the command invoker lacks permissions to invoke a command
    elif isinstance(error, app.MissingPermissions):
        await interaction.response.send_message(format_as_error_msg("You don't have the necessary permissions to use this command!"), ephemeral=True)
        
    # If the command invoker invokes a command in DMs which is restricted to guild only
    elif isinstance(error, app.NoPrivateMessage):
        await interaction.response.send_message(format_as_error_msg("This command is not available for use in DMs! Use it in a server channel instead."), ephemeral=True)
        
    # If the url provided by the command invoker is not Valid/Discord CDN URL
    elif isinstance(error, NotValidURL):
        await interaction.response.send_message(format_as_error_msg("The URL is not valid! Make sure it starts with ``https://cdn.discordapp.com/``"), ephemeral=True)
        
    # If the command invoker invokes an owner-only command
    elif isinstance(error, NotOwner):
        await interaction.response.send_message(format_as_error_msg("This command can only be invoked by the owner!"), ephemeral=True)
    
    # For any unknown/misc exceptions...
    else:
        await interaction.response.send_message(format_as_error_msg("An unknown error occurred during the command execution. Please try again later!"), ephemeral=True)