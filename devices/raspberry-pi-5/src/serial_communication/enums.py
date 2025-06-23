from enum import Enum, unique

from ..utils import map_string_to_enum


@unique
class IncomingCategory(Enum):
    """
    Enum to represent the categories of incoming messages from the Raspberry Pi Pico 2W.
    """
    CHALLENGE = 1
    STATUS = 2
    SERVO_ANGLE = 3
    MOTOR_SPEED = 4
    REQUEST = 5
    BNO08X_TURNS = 6
    ERROR = 7

    @property
    def parsed_name(self) -> str:
        """
        Get the category name in lowercase.

        Returns:
            str: The category name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, category_str: str) -> 'IncomingCategory':
        """
        Convert a string to an IncomingCategory enum value.

        Args:
            category_str (str): The string representation of the incoming category.

        Returns:
            IncomingCategory: The corresponding IncomingCategory enum value.
        """
        return map_string_to_enum(category_str.upper(), cls)


@unique
class Status(Enum):
    """
    Enum to represent the status messages sent and received from the Raspberry Pi Pico 2W.
    """
    START = 1
    STOP = 2
    OK = 3

    @property
    def parsed_name(self) -> str:
        """
        Get the status name in lowercase.

        Returns:
            str: The status name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, status_str: str) -> 'Status':
        """
        Convert a string to a Status enum value.

        Args:
            status_str (str): The string representation of the status.

        Returns:
            Status: The corresponding Status enum value.
        """
        return map_string_to_enum(status_str.upper(), cls)


@unique
class Request(Enum):
    """
    Enum to represent the request messages received from the Raspberry Pi Pico 2W.
    """
    INFERENCE = 1

    @property
    def parsed_name(self) -> str:
        """
        Get the request name in lowercase.

        Returns:
            str: The request name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, request_str: str) -> 'Request':
        """
        Convert a string to a Request enum value.

        Args:
            request_str (str): The string representation of the request.

        Returns:
            Request: The corresponding Request enum value.
        """
        return map_string_to_enum(request_str.upper(), cls)


@unique
class OutgoingCategory(Enum):
    """
    Enum to represent the categories of outgoing messages sent to the Raspberry Pi Pico 2W.
    """
    STATUS = 1
    INFERENCE = 2
    RPLIDAR = 3

    @property
    def parsed_name(self) -> str:
        """
        Get the category name in lowercase.

        Returns:
            str: The category name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, category_str: str) -> 'OutgoingCategory':
        """
        Convert a string to an OutgoingCategory enum value.

        Args:
            category_str (str): The string representation of the outgoing category.

        Returns:
            OutgoingCategory: The corresponding OutgoingCategory enum value.
        """
        return map_string_to_enum(category_str.upper(), cls)


@unique
class RPLIDAR(Enum):
    """
    Enum to represent the RPLIDAR messages sent to the Raspberry Pi Pico 2W.
    """
    FRONT = 1
    LEFT = 2
    RIGHT = 3

    @property
    def parsed_name(self) -> str:
        """
        Get the RPLIDAR name in lowercase.

        Returns:
            str: The RPLIDAR name in lowercase.
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, rplidar_str: str) -> 'RPLIDAR':
        """
        Convert a string to a RPLIDAR enum value.

        Args:
            rplidar_str (str): The string representation of the RPLIDAR message.

        Returns:
            RPLIDAR: The corresponding RPLIDAR enum value.
        """
        return map_string_to_enum(rplidar_str.upper(), cls)
