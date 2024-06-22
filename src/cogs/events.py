import logging
from datetime import datetime
from typing import Literal, Optional

import discord
from discord import Interaction, Embed, Member, Message, app_commands as app
from discord.ext.commands import Cog, Bot

from utils.db_handler import load_database_and_collection

logger = logging.getLogger("snapbot")
coll = load_database_and_collection("afk_data")


class Events(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    def generate_reply_message(self, *, data: dict, type: Literal["Welcome", "Inform"]) -> str:
        """Generates a message for two situations. If the `type` is 'Welcome`, the message will be generated for the use case when the user comes back from being AFK and the bot needs to send a `welcome back response`. On the other hand, if the `type` is 'Inform', the message will generated for the use case when the someone pings an user who is AFK and the bot needs to `inform them` that the user is AFK.

        Parameters
        ----------
        data : `dict`
            A `dict` containing the necessary data about the user who is AFK.
        type : `Literal["Welcome", "Inform"]`
            The message type.

        Returns
        -------
        `str`
        """
        
        timestamp_full_datetime: str = discord.utils.format_dt(data["timestamp"], 'F')
        timestamp_relative_datetime: str = discord.utils.format_dt(data["timestamp"], 'R')
        reason: str = data["reason"]
        user: Member = self.bot.get_user(data["user_id"])
        
        if type == "Welcome":
            return f"Welcome back {user.mention}!\nYou went AFK on {timestamp_full_datetime}\n\n**Reason**: {reason}"
        
        else:
            return f"{user.display_name} went AFK {timestamp_relative_datetime}\n\n**Reason**: {reason}"
        
    async def check_for_afk_user(self, message: Message) -> None:
        """A helper function which checks for afk users in every message. If a message is from a user who was AFK, this function will greet them with a welcome back response.

        Parameters
        ----------
        message : `Message`
            The message sent in the server.
        """
        
        afk_data: Optional[dict] = await coll.find_one({"user_id": message.author.id})
        
        if afk_data is not None:
            await coll.delete_one({"user_id": message.author.id})
            
            try:
                await message.author.edit(nick=afk_data["nickname"])
            
            except discord.Forbidden:
                logger.error(f"Couldn't reset the nickname of the user {message.author.id}")
                
            finally:
                await message.reply(self.generate_reply_message(data=afk_data, type="Welcome"))
                
    async def check_for_afk_user_pings(self, message: Message) -> None:
        """A helper function which checks for afk user's pings in every message. If someone pings an user who is currently AFK, this function will inform them that the user is currently AFK.

        Parameters
        ----------
        message : `Message`
            The message sent in the server.
        """
        
        for user in message.mentions:
            afk_data: Optional[dict] = await coll.find_one({"user_id": user.id})
            
            if afk_data is None:
                continue
            
            else:
                await message.reply(self.generate_reply_message(data=afk_data, type="Inform"))
        
        
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """An event function which reads every message sent on a discord server.

        Parameters
        ----------
        message : `discord.Message`
            The message that is sent in the server.
        """
        
        # With this, the bot won't reply to it's own messages
        if message.author == self.bot.user:
            return
        
        await self.check_for_afk_user(message)
        await self.check_for_afk_user_pings(message)
        

async def setup(bot: Bot) -> None:
    await bot.add_cog(Events(bot))
        
        