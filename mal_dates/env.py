import os
from pathlib import Path
from warnings import warn

from dotenv import load_dotenv

__all__: list[str] = [
    "check_env",
    "DEBUG"
]


def check_env() -> None:
    if not Path(".env").exists():
        raise ValueError("Rename the \".env.template\" file to \".env\" and set the variables!")

    if bool(os.environ.get("USERNAME", False)) is False:
        raise ValueError("You must set a \"USERNAME\" in \".env\"!")

    if bool(os.environ.get("PASSWORD", False)) is False:
        raise ValueError("You must set a \"PASSWORD\" in \".env\"!")


def _check_debug() -> bool:
    if is_debug := bool(os.environ.get("DEBUG")):
        warn("Debug mode enabled!")

    return is_debug


load_dotenv()
DEBUG = _check_debug()
"""Bool representing whether the user is in DEBUG mode."""
