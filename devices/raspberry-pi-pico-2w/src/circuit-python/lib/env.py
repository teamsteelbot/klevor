from os import getenv

from .message import Challenge

class Env:
    """
    Environment variables manager class.

    This class provides methods to access environment variables related to debug mode and challenge type.
    """

    @staticmethod
    def _check_boolean(value: str) -> bool:
        """
        Check if the given string is a valid boolean representation.

        Args:
            value (str): The string to check.

        Returns:
            bool: True if the string represents a boolean value, otherwise False.
        """
        return value in ("true", "false")

    @staticmethod
    def _check_challenge(value: str) -> bool:
        """
        Check if the given string is a valid challenge type.

        Args:
            value (str): The string to check.

        Returns:
            bool: True if the string represents a valid challenge type, otherwise False.
        """
        return value in (Challenge.WITHOUT_OBSTACLES, Challenge.WITH_OBSTACLES)

    @staticmethod
    def get_debug_mode() -> bool:
        """
        Get the debug mode from the environment variable.

        Returns:
            bool: True if debug mode is enabled, otherwise False.
        """
        value = getenv("DEBUG", "false").lower()

        # Check if the value is a valid boolean representation
        if not Env._check_boolean(value):
            raise ValueError(f"Invalid value for DEBUG: {value}. Expected 'true' or 'false'.")

        return value == "true"

    @staticmethod
    def get_challenge() -> str:
        """
        Get the challenge type from the environment variable.

        Returns:
            str: The challenge type, defaulting to 'without_obstacles' if not set.
        """
        value = getenv("CHALLENGE", Challenge.WITHOUT_OBSTACLES).lower()

        # Check if the value is a valid challenge type
        if not Env._check_challenge(value):
            raise ValueError(f"Invalid value for CHALLENGE: {value}. Expected 'without_obstacles' or 'with_obstacles'.")

        return value