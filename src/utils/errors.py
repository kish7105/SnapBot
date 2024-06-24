from discord import app_commands as app


class NotValidURL(app.CheckFailure):
    """This error is raised when the provided url is not valid."""

    def __init__(self, message=None) -> None:
        super().__init__(message or "Not a Valid URL")


class NotOwner(app.CheckFailure):
    """This error is raised when the command invoker is not the bot's owner."""

    def __init__(self, message=None) -> None:
        super().__init__(message or "Not invoked by the owner.")
