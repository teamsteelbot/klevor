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
    SOUTH = 4
    NORTHWEST = 5
    NORTHEAST = 6
    SOUTHWEST = 7
    SOUTHEAST = 8
    WEST_NORTHWEST = 9
    NORTH_NORTHWEST = 10
    EAST_NORTHEAST = 11
    NORTH_NORTHEAST = 12
    WEST_SOUTHWEST = 13
    EAST_SOUTHEAST = 14
    SOUTH_SOUTHWEST = 15
    SOUTH_SOUTHEAST = 16

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
