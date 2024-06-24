from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput

from utils.db_handler import load_database_and_collection
from utils.msg_format import format_as_success_msg

coll = load_database_and_collection("about_data")


class DescriptionModal(Modal, title="About Embed Editor"):
    # This will be the Text Box of the modal
    description = TextInput(
        label="Description",
        style=TextStyle.paragraph,
        placeholder="Enter the description here...",
        max_length=4000,
    )

    # This function will be executed when the user clicks on the submit button
    async def on_submit(self, interaction: Interaction) -> None:
        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "description": self.description.value}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id},
                {"$set": {"description": self.description.value}},
            )

        await interaction.response.send_message(
            format_as_success_msg("Description successfully updated!"), ephemeral=True
        )
