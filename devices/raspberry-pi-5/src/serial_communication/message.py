from enum import Enum, unique

from ..utils import check_type


@unique
class Category(Enum):
    """
    Enum to represent the categories of messages sent and received from the Raspberry Pi Pico.
    """
    CAPTURE_IMAGE = 1
    INFERENCE = 2
    RPLIDAR = 3
    DEBUG = 4
    STATUS = 5

    def get_category_name(self) -> str:
        """
        Get the category name in lowercase.

        Returns:
            str: The category name in lowercase.
        """
        return self.name.lower()

@unique
class Status(Enum):
    """
    Enum to represent the status messages sent and received from the Raspberry Pi Pico.
    """
    START = 1
    STOP = 2
    OK = 3

    def get_status_name(self) -> str:
        """
        Get the status name in lowercase.

        Returns:
            str: The status name in lowercase.
        """
        return self.name.lower()

class Message:
    """
    Class to handle the messages sent and received from the Raspberry Pi Pico.
    """
    # Message header separator
    HEADER_SEPARATOR = ':'

    # Message end character
    END = '\n'

    def __init__(self, category: Category, content: str):
        """
        Initialize the message class.

        Args:
            category (str): The category of the message.
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
    def from_string(msg_str: str) -> 'Message':
        """
        Create a Message object from a string.

        Args:
            message_str (str): The string representation of the message.

        Returns:
            Message: The Message object created from the string.
        """
        # Remove the end character if present
        if msg_str.endswith(Message.END):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(Message.HEADER_SEPARATOR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format")

        # Convert the category string to a Category enum value
        category_name = parts[0].upper()
        if category_name not in Category.__members__:
            raise ValueError(f"Invalid category: {parts[0]}")
        category = Category[category_name]

        # Create and return the Message object
        return Message(category, parts[1])

    @property
    def category(self) -> Category:
        """
        Property to get the message category.

        Returns:
            Category: The category of the message.
        """
        return self.__category

    @category.setter
    def category(self, category: Category):
        """
        Setter for the message category.

        Args:
            category (str): The category of the message.
        """
        # Check the type of message
        check_type(category, Category)
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
        return self.category == Category.STATUS and self.content == Status.START.get_status_name()

    def is_stop(self) -> bool:
        """
        Check if the message is a stop message.

        Returns:
            bool: True if the message is a stop message, False otherwise.
        """
        return self.category == Category.STATUS and self.content == Status.STOP.get_status_name()