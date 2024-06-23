import logging
from datetime import datetime
from typing import Generator, List

import discord
from discord import Interaction, Embed, ButtonStyle, app_commands as app
from discord.ext.commands import Cog, Bot
from reactionmenu import ViewMenu, ViewButton, ViewSelect
import requests

from utils.exc_manager import exception_manager
from utils.msg_format import format_as_error_msg

logger = logging.getLogger("snapbot")


class Define(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    async def cog_app_command_error(self, interaction: Interaction, error: app.AppCommandError) -> None:
        logger.error(error)
        await exception_manager(interaction, error)

    def generate_definition_embeds(
        self, interaction: Interaction, /, *, word: str, data_list: List[dict]
    ) -> Generator[discord.Embed, None, None]:
        """Generates varying amount of discord embeds where each embed display information fetched from the Urban Dictionary which is specified in the form of a list( `data_list` ) for the specified word.

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction
            
        word : `str`
            The word which was queried in the Urban Dictionary.
            
        data_list : `List[dict]`
            The data fetched from the Urban dictionary.

        Yields
        ------
        `Generator[discord.Embed, None, None]`
        """

        for data in data_list:
            
            definition: str = data["definition"]
            example: str = data["example"]
            author: str = data["author"]
            
            embed = (
                Embed(
                    description=f"**{word}**: {definition}\n\n**Example**: {example}",
                    color=discord.Colour.random(),
                    timestamp=datetime.now(),
                )
                .set_author(
                    name=f"Requested By {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url,
                )
                .set_footer(text=f"Written by {author}")
            )

            yield embed

    @app.command(
        name="define",
        description="Query Urban Dictionary for a word's definition and example.",
    )
    @app.describe(word="What do you want to search?")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def define(self, interaction: Interaction, word: str) -> None:
        """A command which allows users to query through the Urban Dictionary for a particular word's definitions and examples.

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction.
            
        word : `str`
            The word provided by the user which will be searched in the Urban Dictionary.
        """
        
        # URL for making http request to Urban Dictionary
        url = f"https://api.urbandictionary.com/v0/define?term={word}"
        
        # Get the response using the URL and run requirement checks like the status code or if the response is empty
        response = requests.get(url)

        if response.status_code != 200:
            await interaction.response.send_message(
                format_as_error_msg("Urban Dictionary API is down! Please try again later."), ephemeral=True
            )
            return

        response_in_json: dict = response.json()

        if not response_in_json["list"]:
            await interaction.response.send_message(
                format_as_error_msg(f"No definitions found for the word: **{word}**"), ephemeral=True
            )
            return

        await interaction.response.defer()
        
        # Get the data list from the response
        data: List[dict] = response_in_json["list"]
        
        embeds: list[discord.Embed] = []
        
        # Adding all the embeds generated from the function to the embeds list defined earlier
        for embed in self.generate_definition_embeds(interaction, word=word, data_list=data):
            embeds.append(embed)
        
        # Create a view menu of type Embed
        view_menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        
        # Defining buttons and select for the view menu
        next_button = ViewButton(
            style=ButtonStyle.secondary,
            label="Next",
            custom_id=ViewButton.ID_NEXT_PAGE,
            emoji="➡️",
        )
        previous_button = ViewButton(
            style=ButtonStyle.secondary,
            label="Previous",
            custom_id=ViewButton.ID_PREVIOUS_PAGE,
            emoji="⬅️",
        )
        go_to_first_button = ViewButton(
            style=ButtonStyle.secondary,
            label="Go to First",
            custom_id=ViewButton.ID_GO_TO_FIRST_PAGE,
            emoji="⏮️"
        )
        go_to_last_button = ViewButton(
            style=ButtonStyle.secondary,
            label="Go to Last",
            custom_id=ViewButton.ID_GO_TO_LAST_PAGE,
            emoji="⏭️"
        )
        go_to = ViewSelect.GoTo(title="Navigate to page...", page_numbers=...)
        
        # Add embeds list as pages to the view menu
        view_menu.add_pages(embeds)
        
        # Adding buttons and select to the view menu
        view_menu.add_buttons([go_to_first_button, previous_button, next_button, go_to_last_button])
        view_menu.add_go_to_select(go_to)
        
        # Starting the view menu
        await view_menu.start()
        

async def setup(bot: Bot) -> None:
    await bot.add_cog(Define(bot))
