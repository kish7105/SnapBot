import json
from typing import Any, Dict


def load_config() -> Dict[str, Any]:
    """Loads configuration data from `config.json`.

    Returns
    -------
    `Dict[str, Any]`
        Configuration data in `dict` format.
    """

    with open("config.json", "r") as file:
        return json.load(file)


def save_config(*, data: Dict[str, Any]) -> None:
    """Writes the provided configuration data to `config.json`.

    Parameters
    ----------
    data : `Dict[str, Any]`
        The data to dump to `config.json`.
    """

    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)
