from typing import Dict, Optional

import discord
from discord import Interaction, TextChannel

from utils.cfg_handler import load_config


def get_channel(interaction: Interaction, /, *, channel: str) -> Optional[TextChannel]:
    """Returns the specified discord server channel. Returns `None` if the channel is not found.

    Parameters
    ----------
    
    interaction: `discord.Interaction`
        Represents a Discord Interaction
        
    channel : `str`
        The name of the text channel to be returned.

    Returns
    -------
    `Optional[TextChannel]`
    """
    
    config_data = load_config()
    channels_data: Dict[str, int] = config_data["server_settings"]["channels"]
    
    if channels_data.get(channel.lower()) is None:
        return None
    
    else:
        return discord.utils.find(lambda c: c.id == channels_data.get(channel.lower()), interaction.guild.channels)
    