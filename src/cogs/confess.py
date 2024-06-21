import logging
from datetime import datetime
from typing import Literal, Optional

import discord
from discord import Interaction, Embed, app_commands as app
from discord.ext.commands import GroupCog, Bot

from utils.checks import is_valid_attachment_url, is_owner
from utils.errors import NotValidURL, NotOwner
from utils.helpers import get_channel
from utils.encryption import encrypt, decrypt

logger = logging.getLogger("snapbot")

@app.guild_only()
class Confession(GroupCog, group_name="confession"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.encrypted_user_id = None
        
    def generate_embed(self, *, confession: str, attachment: Optional[str], type: Literal["Log", "Confession"]) -> Embed:
        """Generates a discord embed which can be used to display the info about the confession to the confessions channel anonymously or to the log channel where it shows the encrypted user Id of the user who made that confession.

        Parameters
        ----------
        confession : `str`
            The confession text provided by the user.
            
        attachment : `Optional[str]`
            The attachment url provided by the user. `None` if nothing is provided by the user.
            
        type : `Literal["Log", "Confession"]`
            The type of embed to generate. `Log` generates a log embed displaying the confession log and `Confession` generates the actual confession embed.

        Returns
        -------
        `discord.Embed`
        """
        
        embed = discord.Embed(
            description=confession,
            color=discord.Color.random(),
            timestamp=datetime.now()
        )

        embed.set_image(url=attachment)
        
        if type == "Confession":
            embed.set_author(name="Anonymous Confession!")
            return embed
        
        else:
            embed.title = "Confession Log"
            embed.add_field(name="Encrypted Key", value=self.encrypted_user_id, inline=False)
            return embed
                
    @app.command(name="post", description="Post an anonymous confession in the server!")
    @app.describe(confession="What are you confessing?", attachment="Enter the link of the attachment here. Make sure it starts with 'https://cdn.discordapp.com/'")
    @app.checks.cooldown(1, 20)
    @is_valid_attachment_url()
    async def post(self, interaction: Interaction, confession: app.Range[str, None, 3500], attachment: Optional[str]) -> None:
        """A command which allows users to post a confession anonymously in the confession's channel of the server.

        Parameters
        ----------
        interaction : `Interaction`
            Represents a Discord Interaction
            
        confession : `app.Range[str, None, 3500]`
            The confession text. Can only be up to 3500 characters long.
            
        attachment : `Optional[str]`
            The attachment's url if the user wishes to attach something with the confession text. Defaults to `None` if user skips this option.
        """
        
        await interaction.response.defer(ephemeral=True)
        
        # Encrypt the command invoker's user ID
        self.encrypted_user_id = encrypt(str(interaction.user.id))
        
        # Get the required channels
        log_channel = get_channel(interaction, channel="log")
        confession_channel = get_channel(interaction, channel="confession")
        
        # Send the embeds to their respective channels
        await log_channel.send(embed=self.generate_embed(confession=confession, attachment=attachment, type="Log"))
        await confession_channel.send(embed=self.generate_embed(confession=confession, attachment=attachment, type="Confession"))
        
        await interaction.followup.send(f"Your confession has been successfully posted in {confession_channel.mention}!")
        
    @app.command(name="decrypt", description="Decrypts the confession using the encryption key")
    @app.describe(encrypted_key="Enter the encrypted key for decryption.")
    @is_owner()
    async def decrypt(self, interaction: Interaction, encrypted_key: str) -> None:
        
        decrypted_message = decrypt(encrypted_key)
        
        # If the decryption fails
        if decrypted_message is None:
            await interaction.response.send_message("Invalid Encryption Key!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Get the log channel
        log_channel = get_channel(interaction, channel="log")
        
        # Send the info to the log channel and send the decrypted message to the user
        await log_channel.send(f"{interaction.user.mention} accessed confession logs just now.")
        await interaction.followup.send(f"Encryption Successful!\n\n**User ID**: {decrypted_message}")
        
    
    @post.error
    async def post_error(self, interaction: Interaction, error: app.AppCommandError) -> None:
        if isinstance(error, app.CommandOnCooldown):
            await interaction.response.send_message(f"Woah.. calm down buddy! Retry after ``{error.retry_after: .2f} seconds``", ephemeral=True)
            
        elif isinstance(error, app.NoPrivateMessage):
            await interaction.response.send_message("This command cannot be used in DMs!", ephemeral=True)
            
        elif isinstance(error, NotValidURL):
            await interaction.response.send_message("The URL you provided is not valid! Make sure the image is sent on discord somewhere and the url for it starts with ``https://cdn.discordapp.com/``", ephemeral=True)
            
        else:
            logger.exception(error)
            await interaction.response.send_message("An unknown error occurred during the command execution! Please try again later.", ephemeral=True)
            
    @decrypt.error
    async def decrypt_error(self, interaction: Interaction, error: app.AppCommandError) -> None:
        if isinstance(error, NotOwner):
            await interaction.response.send_message("Only the bot owner is allowed to use this command!", ephemeral=True)
            
        else:
            logger.exception(error)
            await interaction.response.send_message("An unknown error occurred during the command execution! Please try again later.", ephemeral=True)
        

async def setup(bot: Bot) -> None:
    await bot.add_cog(Confession(bot))