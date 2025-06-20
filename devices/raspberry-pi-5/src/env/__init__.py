import os
from enum import Enum, unique

@unique
class Keys(Enum):
    """
    Enum for environment variable keys.
    """

    DEBUG = 1
    YOLO_VERSION = 2
    CHALLENGE = 3

@unique
class Challenges(Enum):
    """
    Enum to represent different challenges.
    """

    WITH_OBSTACLES = 1
    WITHOUT_OBSTACLES = 2

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
        os.environ[Keys.DEBUG.name] = str(debug).lower()

    @staticmethod
    def set_yolo_version(version: str) -> None:
        """
        Set the YOLO version in the environment variable.

        Args:
            version (str): The YOLO version to set.
        """
        os.environ[Keys.YOLO_VERSION.name] = version

    @staticmethod
    def set_challenge(challenge: Challenges) -> None:
        """
        Set the challenge in the environment variable.

        Args:
            challenge (Challenges): The challenge to set.
        """
        os.environ[Keys.CHALLENGE.name] = challenge.name

    @staticmethod
    def get_debug_mode() -> bool:
        """
        Get the debug mode from the environment variable.

        Returns:
            bool: True if debug mode is enabled, otherwise False.
        """
        return os.getenv(Keys.DEBUG.name, 'false').lower() == 'true'

    @staticmethod
    def get_yolo_version() -> str:
        """
        Get the YOLO version from the environment variable.

        Returns:
            str: The YOLO version, or 'unknown' if not set.
        """
        return os.getenv(Keys.YOLO_VERSION.name, 'unknown')

    @staticmethod
    def get_challenge() -> Challenges:
        """
        Get the challenge from the environment variable.

        Returns:
            Challenges: The challenge enum value.
        """
        challenge_name = os.getenv(Keys.CHALLENGE.name, Challenges.NONE.name)
        for challenge in Challenges:
            if challenge.name == challenge_name:
                return challenge
        return Challenges.NONE
