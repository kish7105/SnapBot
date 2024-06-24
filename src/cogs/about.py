import logging
from typing import Optional

import discord
from discord import Interaction, Embed, Member, app_commands as app
from discord.ext.commands import GroupCog, Bot

from utils.checks import is_valid_attachment_url
from utils.db_handler import load_database_and_collection
from utils.exc_manager import exception_manager
from utils.msg_format import format_as_error_msg, format_as_success_msg

logger = logging.getLogger("snapbot")
coll = load_database_and_collection("about_data")


class About(GroupCog, group_name="about"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_app_command_error(
        self, interaction: Interaction, error: app.AppCommandError
    ) -> None:
        logger.error(error)
        await exception_manager(interaction, error)

    def generate_about_embed(self, *, data: dict) -> Embed:
        """Generates an about embed which displays the user's about data as provided in the `data` parameter

        Parameters
        ----------
        data : `dict`
            The data which will be used to display details in the embed

        Returns
        -------
        `Embed`
        """

        # Check if the color hex code stored in the database is valid
        try:
            color = discord.Color.from_str(data.get("color"))

        # If not valid, set the color to light grey
        except:
            color = discord.Color.light_grey()

        finally:
            embed = Embed(
                title=data.get("title"),
                description=data.get("description"),
                color=color,
            )

            embed.set_image(url=data.get("image"))
            embed.set_thumbnail(url=data.get("thumbnail"))

            if data.get("author_text") is not None:
                embed.set_author(
                    name=data.get("author_text"),
                    url=data.get("author_url"),
                    icon_url=data.get("author_icon"),
                )

            if data.get("footer_text") is not None:
                embed.set_footer(
                    text=data.get("footer_text"), icon_url=data.get("footer_text")
                )

            return embed

    @app.command(
        name="view", description="Display your own OR other user's about embed!"
    )
    @app.describe(user="Whose about embed do you want to view?")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def view(self, interaction: Interaction, user: Optional[Member]) -> None:
        """A command which allows users to view their own OR other user's about embed.

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        user : `Optional[Member]`
            The user whose about embed is requested. Defaults to `None` if not provided
        """

        if user is None:
            user = interaction.user

        about_data: Optional[dict] = await coll.find_one({"user_id": user.id})

        if about_data is None:
            await interaction.response.send_message(
                format_as_error_msg(f"No data found for the user {user.mention}"),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        embed = self.generate_about_embed(data=about_data)
        await interaction.followup.send(embed=embed)

    @app.command(name="edit_title", description="Edits the title of your about embed")
    @app.describe(title="Enter the title here")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_title(
        self, interaction: Interaction, title: app.Range[str, None, 256]
    ) -> None:
        """A command which allows users to edit the title of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        title : `app.Range[str, None, 256]`
            The title of the about embed. Can only be upto 256 characters max
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one({"user_id": interaction.user.id, "title": title})

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"title": title}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Title successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_description", description="Edits the description of your about embed"
    )
    @app.describe(description="Enter the description here")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_description(
        self, interaction: Interaction, description: app.Range[str, None, 4096]
    ) -> None:
        """A command which allows users to edit the description of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        description : `app.Range[str, None, 4096]`
            The description of the about embed. Can only be upto 4096 characters max
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "description": description}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"description": description}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Description successfully updated!"), ephemeral=True
        )

    @app.command(name="edit_color", description="Edits the color of your about embed")
    @app.describe(
        color="Enter the color's hex code here( Exclude the # in the beginning )"
    )
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_color(
        self, interaction: Interaction, color: app.Range[str, 6, 6]
    ) -> None:
        """A command which allows users to edit the color of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        color : `app.Range[str, 6, 6]`
            The hex code of the color of the about embed. Should strictly be 6 characters long
        """

        await interaction.response.defer(ephemeral=True)

        # Check if the hex code provided by the user is valid
        try:
            discord.Color.from_str(f"#{color}")

        except:
            await interaction.followup.send(format_as_error_msg("Invalid Hex Code!"))

        else:
            if await coll.find_one({"user_id": interaction.user.id}) is None:
                await coll.insert_one(
                    {"user_id": interaction.user.id, "color": f"#{color}"}
                )

            else:
                await coll.update_one(
                    {"user_id": interaction.user.id}, {"$set": {"color": f"#{color}"}}
                )

            await interaction.followup.send(
                format_as_success_msg("Color successfully updated!")
            )

    @app.command(name="edit_image", description="Edits the image of your about embed")
    @app.describe(
        attachment="Enter the image url here. Make sure it starts with 'https://cdn.discordapp.com/'"
    )
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    @is_valid_attachment_url()
    async def edit_image(self, interaction: Interaction, attachment: str) -> None:
        """A command which allows users to edit the image of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        attachment : `str`
            The image attachment URL of the about embed.
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one({"user_id": interaction.user.id, "image": attachment})

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"image": attachment}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Image successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_thumbnail", description="Edits the thumbnail of your about embed"
    )
    @app.describe(
        attachment="Enter the thumbnail url here. Make sure it starts with 'https://cdn.discordapp.com/'"
    )
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    @is_valid_attachment_url()
    async def edit_thumbnail(self, interaction: Interaction, attachment: str) -> None:
        """A command which allows users to edit the thumbnail of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        attachment : `str`
            The thumbnail attachment URL of the about embed.
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "thumbnail": attachment}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"thumbnail": attachment}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Thumbnail successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_author_icon", description="Edits the Author Icon of your about embed"
    )
    @app.describe(
        attachment="Enter the author icon url here. Make sure it starts with 'https://cdn.discordapp.com/'"
    )
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    @is_valid_attachment_url()
    async def edit_author_icon(self, interaction: Interaction, attachment: str) -> None:
        """A command which allows users to edit the author icon of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        attachment : `str`
            The author icon attachment URL of the about embed.
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "author_icon": attachment}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"author_icon": attachment}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Author Icon successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_footer_icon", description="Edits the Footer Icon of your about embed"
    )
    @app.describe(
        attachment="Enter the footer icon url here. Make sure it starts with 'https://cdn.discordapp.com/'"
    )
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    @is_valid_attachment_url()
    async def edit_footer_icon(self, interaction: Interaction, attachment: str) -> None:
        """A command which allows users to edit the footer icon of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        attachment : `str`
            The footer icon attachment URL of the about embed.
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "footer_icon": attachment}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"footer_icon": attachment}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Footer Icon successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_author_url", description="Edits the Author URL of your about embed"
    )
    @app.describe(url="Enter the url here.")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_author_url(self, interaction: Interaction, url: str) -> None:
        """A command which allows users to edit the author url of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        url : `str`
            The author url of the about embed.
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one({"user_id": interaction.user.id, "author_url": url})

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"author_url": url}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Author URL successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_author_text", description="Edits the Author text of your about embed"
    )
    @app.describe(author_text="Enter the author text here")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_author_text(
        self, interaction: Interaction, author_text: app.Range[str, None, 256]
    ) -> None:
        """A command which allows users to edit the author text of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        author_text : `app.Range[str, None, 256]`
            The author text of the about embed. Can only be upto 256 characters max
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "author_text": author_text}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"author_text": author_text}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Author Text successfully updated!"), ephemeral=True
        )

    @app.command(
        name="edit_footer_text", description="Edits the Footer text of your about embed"
    )
    @app.describe(footer_text="Enter the footer text here")
    @app.checks.cooldown(1, 10)
    @app.guild_only()
    async def edit_footer_text(
        self, interaction: Interaction, footer_text: app.Range[str, None, 2048]
    ) -> None:
        """A command which allows users to edit the footer text of their about embed

        Parameters
        ----------
        interaction : `discord.Interaction`
            Represents a Discord Interaction

        footer_text : `app.Range[str, None, 2048]`
            The footer text of the about embed. Can only be upto 2048 characters max
        """

        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "footer_text": footer_text}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id}, {"$set": {"footer_text": footer_text}}
            )

        await interaction.response.send_message(
            format_as_success_msg("Footer Text successfully updated!"), ephemeral=True
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(About(bot))
