from enum import Enum, unique

from ..utils import check_type

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

    def get_name(self) -> str:
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
        category_name = category_str.upper()
        if category_name not in cls.__members__:
            raise ValueError(f"Invalid incoming category: {category_str}")
        return cls[category_name]

@unique
class Status(Enum):
    """
    Enum to represent the status messages sent and received from the Raspberry Pi Pico 2W.
    """
    START = 1
    STOP = 2
    OK = 3

    def get_name(self) -> str:
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
        status_name = status_str.upper()
        if status_name not in cls.__members__:
            raise ValueError(f"Invalid status: {status_str}")
        return cls[status_name]

@unique
class Request(Enum):
    """
    Enum to represent the request messages received from the Raspberry Pi Pico 2W.
    """
    INFERENCE = 1

    def get_name(self) -> str:
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
        request_name = request_str.upper()
        if request_name not in cls.__members__:
            raise ValueError(f"Invalid request: {request_str}")
        return cls[request_name]

@unique
class OutgoingCategory(Enum):
    """
    Enum to represent the categories of outgoing messages sent to the Raspberry Pi Pico 2W.
    """
    STATUS = 1
    INFERENCE = 2
    RPLIDAR = 3

    def get_name(self) -> str:
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
        category_name = category_str.upper()
        if category_name not in cls.__members__:
            raise ValueError(f"Invalid outgoing category: {category_str}")
        return cls[category_name]

@unique
class RPLIDAR(Enum):
    """
    Enum to represent the RPLIDAR messages sent to the Raspberry Pi Pico 2W.
    """
    FRONT = 1
    LEFT = 2
    RIGHT = 3

    def get_name(self) -> str:
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
        rplidar_name = rplidar_str.upper()
        if rplidar_name not in cls.__members__:
            raise ValueError(f"Invalid RPLIDAR message: {rplidar_str}")
        return cls[rplidar_name]

class IncomingMessage:
    """
    Class to handle the messages received from the Raspberry Pi Pico 2W.
    """
    # Message header separator
    HEADER_SEPARATOR = ':'

    # Message end character
    END = '\n'

    def __init__(self, category: IncomingCategory, content: str):
        """
        Initialize the incomming message class.

        Args:
            category (IncomingCategory): The category of the message.
            content (str): The content of the message.
        """
        self.category = category
        self.content = content

    def __str__(self) -> str:
        """
        String representation of the message.
        """
        return f"{self.__category}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

    @staticmethod
    def from_string(msg_str: str) -> 'IncomingMessage':
        """
        Create a Message object from a string.

        Args:
            msg_str (str): The string representation of the message.

        Returns:
            Message: The Message object created from the string.
        """
        # Remove the end character if present
        if msg_str.endswith(IncomingMessage.END):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(IncomingMessage.HEADER_SEPARATOR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid incoming message format")

        # Convert the category string to a Category enum value
        category = IncomingCategory.from_string(parts[0])

        # Create and return the Message object
        return IncomingMessage(category, parts[1])

    @property
    def category(self) -> IncomingCategory:
        """
        Property to get the message category.

        Returns:
            IncomingCategory: The category of the message.
        """
        return self.__category

    @category.setter
    def category(self, category: IncomingCategory):
        """
        Setter for the message category.

        Args:
            category (IncomingCategory): The category of the message.
        """
        # Check the type of message
        check_type(category, IncomingCategory)
        self.__category = category

    @property
    def content(self) -> str:
        """
        Get the message content.

        Returns:
            str: The content of the message.
        """
        return self.__content

    @content.setter
    def content(self, content: str):
        """
        Setter for the message content.

        Args:
            content (str): The content of the message.
        """
        # Check the type of content
        check_type(content, str)
        self.__content = content

    def is_start(self) -> bool:
        """
        Check if the message is a start message.

        Returns:
            bool: True if the message is a start message, False otherwise.
        """
        return self.category == IncomingCategory.STATUS and self.content == Status.START.get_name()

    def is_challenge(self) -> bool:
        """
        Check if the message is a challenge message.

        Returns:
            bool: True if the message is a challenge message, False otherwise.
        """
        return self.category == IncomingCategory.CHALLENGE

    def is_stop(self) -> bool:
        """
        Check if the message is a stop message.

        Returns:
            bool: True if the message is a stop message, False otherwise.
        """
        return self.category == IncomingCategory.STATUS and self.content == Status.STOP.get_name()

    def is_error(self) -> bool:
        """
        Check if the message is an error message.

        Returns:
            bool: True if the message is an error message, False otherwise.
        """
        return self.category == IncomingCategory.ERROR

class OutgoingMessage:
    """
    Class to handle the messages sent to the Raspberry Pi Pico 2W.
    """
    # Message header separator
    HEADER_SEPARATOR = ':'

    # Content header separator
    CONTENT_HEADER_SEPARATOR = '='

    # Content separator
    CONTENT_SEPARATOR = ','

    # Message end character
    END = '\n'

    def __init__(self, category: OutgoingCategory, content: str):
        """
        Initialize the outgoing message class.

        Args:
            category (OutgoingCategory): The category of the message.
            content (str): The content of the message.
        """
        self.category = category
        self.content = content

    def __str__(self) -> str:
        """
        String representation of the message.
        """
        return f"{self.__category}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

    @staticmethod
    def from_string(msg_str: str) -> 'OutgoingMessage':
        """
        Create a Message object from a string.

        Args:
            msg_str (str): The string representation of the message.

        Returns:
            Message: The Message object created from the string.
        """
        # Remove the end character if present
        if msg_str.endswith(OutgoingMessage.END):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(OutgoingMessage.HEADER_SEPARATOR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid outgoing message format")

        # Convert the category string to a Category enum value
        category = OutgoingCategory.from_string(parts[0])

        # Create and return the Message object
        return OutgoingMessage(category, parts[1])

    @property
    def category(self) -> OutgoingCategory:
        """
        Property to get the message category.

        Returns:
            OutgoingCategory: The category of the message.
        """
        return self.__category

    @category.setter
    def category(self, category: OutgoingCategory):
        """
        Setter for the message category.

        Args:
            category (OutgoingCategory): The category of the message.
        """
        # Check the type of message
        check_type(category, OutgoingCategory)
        self.__category = category

    @property
    def content(self) -> str:
        """
        Get the message content.

        Returns:
            str: The content of the message.
        """
        return self.__content

    @content.setter
    def content(self, content: str):
        """
        Setter for the message content.

        Args:
            content (str): The content of the message.
        """
        # Check the type of content
        check_type(content, str)
        self.__content = content