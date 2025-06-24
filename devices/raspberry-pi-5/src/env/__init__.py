import os

from .enums import Challenge, Key
from ..utils import map_string_to_enum


class Env:
    """
    Environment variables manager class.

    This class provides methods to get environment variables related to debug mode and YOLO version.
    """

    @staticmethod
    def set_debug_mode(debug: bool) -> None:
        """
        Set the debug mode in the environment variable.

        Args:
            debug (bool): True to enable debug mode, False to disable.
        """
        os.environ[Key.DEBUG.name] = str(debug).lower()

    @staticmethod
    def set_yolo_version(version: str) -> None:
        """
        Set the YOLO version in the environment variable.

        Args:
            version (str): The YOLO version to set.
        """
        os.environ[Key.YOLO_VERSION.name] = version

    @staticmethod
    def set_challenge(challenge: Challenge) -> None:
        """
        Set the challenge in the environment variable.

        Args:
            challenge (Challenge): The challenge to set.
        """
        os.environ[Key.CHALLENGE.name] = challenge.name

    @staticmethod
    def get_debug_mode() -> bool:
        """
        Get the debug mode from the environment variable.

        Returns:
            bool: True if debug mode is enabled, otherwise False.
        """
        return os.getenv(Key.DEBUG.name, 'false').lower() == 'true'

    @staticmethod
    def get_yolo_version() -> str:
        """
        Get the YOLO version from the environment variable.

        Returns:
            str: The YOLO version, or 'unknown' if not set.
        """
        return os.getenv(Key.YOLO_VERSION.name, 'unknown')

    @staticmethod
    def get_challenge() -> Challenge:
        """
        Get the challenge from the environment variable.

        Returns:
            Challenge: The challenge enum value.
        """
        challenge_name = os.getenv(Key.CHALLENGE.name, "unknown")
        return map_string_to_enum(challenge_name.upper(), Challenge)

    @staticmethod
    def has_challenge() -> bool:
        """
        Check if the challenge environment variable is set.

        Returns:
            bool: True if the challenge is set, otherwise False.
        """
        return Key.CHALLENGE.name in os.environ
