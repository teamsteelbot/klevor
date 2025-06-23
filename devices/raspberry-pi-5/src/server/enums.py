from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class Tag(Enum):
    """
    Enum to represent the tags of messages sent and received from the server.
    This is used for categorizing or filtering messages based on their type.
    """
    CONNECTION_STATUS = 1
    SERIAL_INCOMING_MESSAGE = 2
    SERIAL_OUTGOING_MESSAGE = 3
    ORIGINAL_IMAGE = 4
    MODEL_G_IMAGE = 5
    MODEL_M_IMAGE = 6
    MODEL_R_IMAGE = 7
    RPLIDAR_MEASURES = 8
    STOP_EVENT = 9
    PARKING_EVENT = 10

    @staticmethod
    def from_string(tag_str: str) -> "Tag":
        """
        Convert a string to a Tag enum value.

        Args:
            tag_str (str): The string representation of the tag.

        Returns:
            Tag: The corresponding Tag enum value.
        """
        return map_string_to_enum(tag_str.upper(), Tag)
