import logging
from datetime import datetime
from typing import List, Literal, Optional, Union

import discord
from discord import Interaction, Embed, Member, User, ButtonStyle, app_commands as app
from discord.ext.commands import Cog, Bot
from reactionmenu import ViewMenu, ViewButton

from utils.exc_manager import exception_manager

logger = logging.getLogger("snapbot")


class Avatar(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    async def cog_app_command_error(self, interaction: Interaction, error: app.AppCommandError) -> None:
        logger.error(error)
        await exception_manager(interaction, error)

    def generate_avatar_embed(
        self,
        interaction: Interaction,
        /,
        *,
        user: Union[Member, User],
        avatar_type: Literal["Global", "Display", "Guild"],
    ) -> Embed:
        """Generates a discord embed which displays the specified `user`'s discord avatar according to the `avatar_type`.

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction.

        user : `Union[discord.Member, discord.User]`
            Represents a Discord Member or an User depending upon the value passed in.

        avatar_type : `Literal["Global", "Display", "Guild"]`
            Represents the avatar type. Can be either `Global`, `Display` or `Guild`.

        Returns
        -------
        `discord.Embed`
        """

        embed = Embed(
            title=f"{user.display_name}'s {avatar_type} Avatar!",
            color=discord.Color.random(),
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )

        if avatar_type == "Global":
            embed.set_image(url=user.avatar.url)

        elif avatar_type == "Guild":
            embed.set_image(url=user.guild_avatar.url)

        else:
            embed.set_image(url=user.display_avatar.url)

        return embed

    @app.command(name="avatar", description="Displays the requested user's avatar")
    @app.describe(user="Whose avatar do you want to view?")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def avatar(
        self, interaction: Interaction, user: Optional[Union[Member, User]]
    ) -> None:
        """A basic slash command which allows users to view their own or other user's discord avatar.

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        user : `Optional[Union[Member, User]]`
            Represents the user whose avatar is being requested. The user can also be a `discord.Member` if the user is from the same guild as displayed using `discord.Interaction.guild` method . Defaults to `None` if not provided.
        """

        await interaction.response.defer()

        if user is None:
            user = interaction.user

        embeds: List[Embed] = []

        # If the global avatar is not None
        if user.avatar is not None:
            embeds.append(
                self.generate_avatar_embed(interaction, user=user, avatar_type="Global")
            )

        # If the user is an instance of a `discord.Member` class and the guild specific avatar is not None
        if isinstance(user, Member) and user.guild_avatar is not None:
            embeds.append(
                self.generate_avatar_embed(interaction, user=user, avatar_type="Guild")
            )

        # ? In the conditional statements below, an embed is made using the avatar_type as "Display". It is because the methods other than `display_avatar` returns None if the user doesn't have a discord avatar and is using the default avatar provided by discord. In that case, `display_avatar` shall be used.

        # If the user is an instance of a `discord.User` class and the global avatar is None
        if isinstance(user, User) and user.avatar is None:
            embeds.append(
                self.generate_avatar_embed(
                    interaction, user=user, avatar_type="Display"
                )
            )

        # If the user is an instance of a `discord.Member` class and both the global and guild specific avatar are None
        if (
            isinstance(user, Member)
            and user.avatar is None
            and user.guild_avatar is None
        ):
            embeds.append(
                self.generate_avatar_embed(
                    interaction, user=user, avatar_type="Display"
                )
            )

        view_menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        # Adding embeds list as pages to the view menu
        view_menu.add_pages(embeds)

        # Defining buttons for the view menu
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

        # Adding buttons to the view menu
        view_menu.add_buttons([previous_button, next_button])

        # Starting the view menu
        await view_menu.start()


async def setup(bot: Bot) -> None:
    await bot.add_cog(Avatar(bot))
