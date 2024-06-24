from json import load
from discord import Interaction, app_commands as app

from utils.errors import NotValidURL, NotOwner
from utils.cfg_handler import load_config

config_data = load_config()


def is_valid_attachment_url():
    """A check which returns `True` if the url provided is a valid discord cdn url. Else, `False`."""

    def predicate(interaction: Interaction) -> bool | NotValidURL:
        if interaction.namespace.attachment is None:
            return True

        if interaction.namespace.attachment.startswith("https://cdn.discordapp.com/"):
            return True
        raise NotValidURL()

    return app.check(predicate)


def is_owner():
    """A check which returns `True` if the command invoker is the bot owner. Else, `False`."""

    def predicate(interaction: Interaction) -> bool | NotOwner:
        if interaction.user.id == config_data["bot"]["owner"]:
            return True

        return False

    return app.check(predicate)
