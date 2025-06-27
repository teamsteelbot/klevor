from .constants import HEADER_SEPARATOR_CHAR, END_CHAR
from .enums import IncomingCategory, OutgoingCategory, Status
from ..utils import is_instance


class IncomingMessage:
    """
    Class to handle the messages received from the Raspberry Pi Pico 2W.
    """

    def __init__(self, category: IncomingCategory, content: str):
        """
        Initialize the incoming message class.

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
        return f"{self.__category.parsed_name}{HEADER_SEPARATOR_CHAR}{self.__content}{END_CHAR}"

    def __eq__(self, other: 'IncomingMessage') -> bool:
        """
        Check equality of two IncomingMessage objects.

        Args:
            other (IncomingMessage): The other IncomingMessage object to compare with.
        Returns:
            bool: True if both messages have the same category and content, False otherwise.
        """
        return self.category == other.category and self.content == other.content

    @staticmethod
    def from_string(msg_str: str) -> 'IncomingMessage':
        """
        Create a Message object from a string.

        Args:
            msg_str (str): The string representation of the message.
        Returns:
            Message: The Message object created from the string.
        Raises:
            ValueError: If the string does not match the expected format.
        """
        # Remove the end character if present
        if msg_str.endswith(END_CHAR):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(HEADER_SEPARATOR_CHAR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid incoming message format")

        # Convert the category string to a Category enum value
        try:
            category = IncomingCategory.from_string(parts[0])

        except ValueError:
            raise ValueError(f"Invalid category in incoming message: {parts[0]}")

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
        is_instance(category, IncomingCategory)
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
        is_instance(content, str)
        self.__content = content

    def is_start(self) -> bool:
        """
        Check if the message is a start message.

        Returns:
            bool: True if the message is a start message, False otherwise.
        """
        return self.category == IncomingCategory.STATUS and self.content == Status.START.parsed_name

    def is_challenge(self) -> bool:
        """
        Check if the message is a challenge message.

        Returns:
            bool: True if the message is a challenge message, False otherwise.
        """
        return self.category == IncomingCategory.CHALLENGE

    def is_error(self) -> bool:
        """
        Check if the message is an error message.

        Returns:
            bool: True if the message is an error message, False otherwise.
        """
        return self.category == IncomingCategory.ERROR

    def is_confirmation(self) -> bool:
        """
        Check if the message is a confirmation message.

        Returns:
            bool: True if the message is a confirmation message, False otherwise.
        """
        return self.category == IncomingCategory.STATUS and self.content == Status.OK.parsed_name

    def is_bno08x_yaw(self) -> bool:
        """
        Check if the message is a BNO08X yaw message.

        Returns:
            bool: True if the message is a BNO08X yaw message, False otherwise.
        """
        return self.category == IncomingCategory.BNO08X_YAW

    def is_bno08x_turns(self) -> bool:
        """
        Check if the message is a BNO08X turns message.

        Returns:
            bool: True if the message is a BNO08X turns message, False otherwise.
        """
        return self.category == IncomingCategory.BNO08X_TURNS


class OutgoingMessage:
    """
    Class to handle the messages sent to the Raspberry Pi Pico 2W.
    """

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
        return f"{self.__category.parsed_name}{HEADER_SEPARATOR_CHAR}{self.__content}{END_CHAR}"

    def __eq__(self, other: 'OutgoingMessage') -> bool:
        """
        Check equality of two OutgoingMessage objects.

        Args:
            other (OutgoingMessage): The other OutgoingMessage object to compare with.
        Returns:
            bool: True if both messages have the same category and content, False otherwise.
        """
        return self.category == other.category and self.content == other.content

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
        if msg_str.endswith(END_CHAR):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(HEADER_SEPARATOR_CHAR, 1)
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
        is_instance(category, OutgoingCategory)
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
        is_instance(content, str)
        self.__content = content