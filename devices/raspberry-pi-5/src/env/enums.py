from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class Key(Enum):
    """
    Enum for environment variable keys.
    """

    DEBUG = 1
    YOLO_VERSION = 2
    CHALLENGE = 3


@unique
class Challenge(Enum):
    """
    Enum to represent different challenges.
    """

    WITH_OBSTACLES = 1
    WITHOUT_OBSTACLES = 2

    @classmethod
    def from_string(cls, challenge_str: str) -> 'Challenge':
        """
        Convert a string to a Challenge enum value.

        Args:
            challenge_str (str): The string representation of the challenge.

        Returns:
            Challenge: The corresponding Challenge enum value.
        """
        return map_string_to_enum(challenge_str.upper(), cls)