from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class Direction(Enum):
    """
    Enum to represent the different directions that RPLidar can face.
    """
    NORTH = 1
    WEST = 2
    EAST = 3
    NORTHWEST = 4
    NORTHEAST = 5
    SOUTHWEST = 6
    SOUTHEAST = 7
    WEST_NORTHWEST = 8
    NORTH_NORTHWEST = 9
    EAST_NORTHEAST = 10
    NORTH_NORTHEAST = 11
    WEST_SOUTHWEST = 12
    EAST_SOUTHEAST = 13

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
