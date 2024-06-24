from discord import Embed, Interaction, TextStyle
from discord.ui import Modal, TextInput

from utils.db_handler import load_database_and_collection
from utils.msg_format import format_as_success_msg

coll = load_database_and_collection("about_data")


class FooterTextModal(Modal, title="About Embed Editor"):
    # This will be the Text Box of the modal
    footer_text = TextInput(
        label="Footer Text",
        style=TextStyle.paragraph,
        placeholder="Enter the footer text here...",
        max_length=2048,
    )

    # This function will be executed when the user clicks on the submit button
    async def on_submit(self, interaction: Interaction) -> None:
        if await coll.find_one({"user_id": interaction.user.id}) is None:
            await coll.insert_one(
                {"user_id": interaction.user.id, "footer_text": self.footer_text.value}
            )

        else:
            await coll.update_one(
                {"user_id": interaction.user.id},
                {"$set": {"footer_text": self.footer_text.value}},
            )

        await interaction.response.send_message(
            format_as_success_msg("Footer Text successfully updated!"), ephemeral=True
        )
