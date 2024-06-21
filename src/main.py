import asyncio
import logging
import logging.config
import os
from typing import List

from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

from utils.cfg_handler import load_config

# Loading environment variables from '.env' and configuration data from 'config.json'
load_dotenv()
config_data = load_config()


# Configuring the logger

# if the logs folder is not present in the root directory, create it using mkdir
if not os.path.exists("logs"):
    os.mkdir("logs")

class EventsFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR


logging.config.dictConfig(config_data["logging"])
logger = logging.getLogger("snapbot")


# Initialising SnapBot class
class SnapBot(Bot):
    """A Class which represents and initialises SnapBot.

    Parameters
    ----------
    Bot : `commands.Bot`
        Represents a Discord Bot.
    """

    def __init__(self) -> None:
        super().__init__(
            command_prefix=config_data["bot"]["prefix"],
            intents=Intents.all(),
            help_command=config_data["bot"]["help_command"],
        )

    async def setup_hook(self) -> None:
        """To perform any asynchronous setup after the bot is logged in but before it is connected to the WebSocket."""

        # Without this, the application commands won't show up on Discord
        await self.tree.sync()

    async def on_ready(self) -> None:
        """This function is called when the bot's internal cache is ready."""

        # Logging info to the console and 'events.log``
        print(f"Logged in as {self.user}")
        logger.info(f"Logged in as {self.user}")


bot = SnapBot()


async def find_and_load_commands() -> None:
    """Finds and loads the cogs/commands to the bot."""

    extensions: List[str] = []

    for file in os.listdir("src/cogs"):
        # Ignore '__pycache__' directory and '__init__.py' file
        if file in ["__pycache__", "__init__.py"]:
            continue

        elif file.endswith(".py"):
            # file[:-3] = filename without .py extension
            extensions.append(f"cogs.{file[:-3]}")

        else:
            continue

    for extension in extensions:
        await bot.load_extension(extension)


async def main() -> None:
    """The main function responsible for starting the bot."""

    await find_and_load_commands()
    await bot.start(os.getenv("TEST_TOKEN"))


if __name__ == "__main__":
    try:
        asyncio.run(main())

    # To prevent flooding of errors when doing Ctrl + C to stop the bot
    except KeyboardInterrupt:
        print("\nShutting down...\n")
