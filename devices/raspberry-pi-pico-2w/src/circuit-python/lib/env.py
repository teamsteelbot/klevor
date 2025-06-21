from os import getenv

class Challenge:
    """
    Class to represent the enum challenge messages sent and received from the Raspberry Pi Pico.
    """
    WITH_OBSTACLES = "with_obstacles"
    WITHOUT_OBSTACLES = "without_obstacles"

    @staticmethod
    def from_string(challenge_str: str) -> 'Challenge':
        """
        Convert a string to a Challenge enum value.

        Args:
            challenge_str (str): The string representation of the challenge.

        Returns:
            Challenge: The corresponding Challenge enum value.
        """
        challenge_name = challenge_str.upper()
        if challenge_name not in [Challenge.WITH_OBSTACLES, Challenge.WITHOUT_OBSTACLES]:
            raise ValueError(f"Invalid challenge: {challenge_str}")
        return Challenge[challenge_name]


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
    def get_movement_mode() -> bool:
        """
        Get the movement mode from the environment variable.

        Returns:
            bool: True if movement mode is enabled, otherwise False.
        """
        value = getenv("MOVEMENT", "false").lower()

        # Check if the value is a valid boolean representation
        if not Env._check_boolean(value):
            raise ValueError(f"Invalid value for MOVEMENT: {value}. Expected 'true' or 'false'.")

        return value == "true"

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