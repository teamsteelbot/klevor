from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class Direction(Enum):
    """
    Enum to represent the different directions that RPLidar can face.
    """
    FRONT = 1
    LEFT = 2
    RIGHT = 3

    def get_name(self) -> str:
        """
        Get the direction name in lowercase.

        Returns:
            str: The direction name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, direction_str: str) -> 'Direction':
        """
        Convert a string to a Direction enum value.

        Args:
            direction_str (str): The string representation of the direction.
        Returns:
            Direction: The corresponding Direction enum value.
        """
        return map_string_to_enum(direction_str.upper(), cls)
