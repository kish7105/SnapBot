import logging
from datetime import datetime
from typing import Optional

import discord
from discord import Interaction, Embed, Member, app_commands as app
from discord.ext.commands import Cog, Bot

from utils.db_handler import load_database_and_collection
from utils.exc_manager import exception_manager

logger = logging.getLogger("snapbot")
coll = load_database_and_collection("afk_data")


class AFK(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    async def cog_app_command_error(self, interaction: Interaction, error: app.AppCommandError) -> None:
        logger.error(error)
        await exception_manager(interaction, error)
        
    def generate_afk_embed(self, *, user: Member, reason: str) -> Embed:
        """Generates a discord embed which displays the details about the user going AFK in the server.

        Parameters
        ----------
        user : `discord.Member`
            Represents the user who is going AFK.
            
        reason : `str`
            Represents the reason why user is going AFK.

        Returns
        -------
        `Embed`
        """
        
        timestamp: str = discord.utils.format_dt(datetime.now(), 'R')
        
        embed = Embed(
            description=f"{user.mention} went AFK {timestamp}",
            color=discord.Colour.random(),
            timestamp=datetime.now()
        )
        
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        return embed
    
    def generate_welcome_back_msg(self, *, data: dict) -> str:
        """Generates a message for welcoming the user when they come back from being AFK.

        Parameters
        ----------
        data : `dict`
            A `dict` containing the necessary data about the user when they went AFK.

        Returns
        -------
        `str`
        """
        
        timestamp: str = discord.utils.format_dt(data["timestamp"], 'F')
        reason: str = data["reason"]
        user: Member = self.bot.get_user(data["user_id"])
        
        return f"Welcome back {user.mention}!\nYou went AFK at {timestamp}\n\n**Reason**: {reason}"
        
        
    @app.command(name="afk", description="Sets your status to AFK in the server.")
    @app.describe(reason="Why are you going AFK?")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def afk(self, interaction: Interaction, reason: app.Range[str, None, 200] = "Not Provided") -> None:
        """A command which allows users to set their status to AFK in the server. The bot will basically remind any user who pings/mentions an AFK user in the server to let them know that the person they are trying to contact is AFK.

        Parameters
        ----------
        interaction : `Interaction`
            Represents a Discord Interaction
            
        reason : `Optional[app.Range[str, None, 200]]`
            Represents the reason why user is going AFK. Defaults to `Not provided` if not set and can only be upto 200 characters max.
        """
        
        await interaction.response.defer()
        user = interaction.user
        
        # Fetching data from the database
        afk_data: Optional[dict] = await coll.find_one({"user_id": user.id})
        
        # If the fetched data is None, it means the user wasn't afk before using this command
        # Basically, we have to set the status to AFK in this case
        if afk_data is None:
            await coll.insert_one({
                "user_id": user.id,  # User's ID
                "reason": reason,  # Reason
                "timestamp": datetime.now(),  # Datetime object
                "nickname": user.nick  # User's nickname
            })
            embed = self.generate_afk_embed(user=user, reason=reason)
            
            try:
                await user.edit(nick=f"[AFK] {user.display_name}")
                
            except discord.Forbidden:
                logger.error(f"Couldn't change the nickname of the user {user.id}")
                
            finally:
                await interaction.followup.send(embed=embed)
            
        # If the fetched data is not None, it means the user was afk before using this command
        # So, we can just remove the afk status here in this case
        else:
            await coll.delete_one({"user_id": user.id})
            try:
                await user.edit(nick=afk_data["nickname"])
            
            except discord.Forbidden:
                logger.error(f"Couldn't reset the nickname of the user {user.id}")
                
            finally:
                await interaction.followup.send(self.generate_welcome_back_msg(data=afk_data))
                

async def setup(bot: Bot) -> None:
    await bot.add_cog(AFK(bot))
            
            
            