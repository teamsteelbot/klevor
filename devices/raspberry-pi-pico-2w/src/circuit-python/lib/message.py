from .enums import IncomingCategory, OutgoingCategory

# Message header separator
HEADER_SEPARATOR_CHAR = ':'

# Message end character
END_CHAR = '\x04'


class IncomingMessage:
    """
    Class to handle the messages received from the Raspberry Pi 5.
    """

    def __init__(self, category: str, content: str):
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
        return f"{self.__category}{HEADER_SEPARATOR_CHAR}{self.__content}{END_CHAR}"

    def __eq__(self, other: 'IncomingMessage') -> bool:
        """
        Check if two messages are equal.

        Args:
            other (IncomingMessage): The other message to compare with.

        Returns:
            bool: True if the messages are equal, False otherwise.
        """
        return (self.category == other.category and
                self.content == other.content)

    @staticmethod
    def from_string(msg_str: str) -> 'IncomingMessage':
        """
        Create a IncomingMessage object from a string.

        Args:
            msg_str (str): The string representation of the message.

        Returns:
            IncomingMessage: The IncomingMessage object created from the string.
        """
        # Remove the end character if present
        if msg_str.endswith(END_CHAR):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(HEADER_SEPARATOR_CHAR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid incoming message format")

        # Convert the category string to a Category enum value
        category = IncomingCategory.from_string(parts[0])

        # Create and return the IncomingMessage object
        return IncomingMessage(category, parts[1])

    @property
    def category(self) -> str:
        """
        Property to get the message category.

        Returns:
            str: The category of the message.
        """
        return self.__category

    @category.setter
    def category(self, category: str):
        """
        Setter for the message category.

        Args:
            category (str): The category of the message.
        """
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
        self.__content = content


class OutgoingMessage:
    """
    Class to handle the messages sent to the Raspberry Pi 5.
    """

    def __init__(self, category: str, content: str):
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
        return f"{self.__category}{HEADER_SEPARATOR_CHAR}{self.__content}{END_CHAR}"

    def __eq__(self, other: 'OutgoingMessage') -> bool:
        """
        Check if two messages are equal.

        Args:
            other (OutgoingMessage): The other message to compare with.

        Returns:
            bool: True if the messages are equal, False otherwise.
        """
        return (self.category == other.category and
                self.content == other.content)

    @staticmethod
    def from_string(msg_str: str) -> 'OutgoingMessage':
        """
        Create a OutgoingMessage object from a string.

        Args:
            msg_str (str): The string representation of the message.

        Returns:
            OutgoingMessage: The OutgoingMessage object created from the string.
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

        # Create and return the OutgoingMessage object
        return OutgoingMessage(category, parts[1])

    @property
    def category(self) -> str:
        """
        Property to get the message category.

        Returns:
            str: The category of the message.
        """
        return self.__category

    @category.setter
    def category(self, category: str):
        """
        Setter for the message category.

        Args:
            category (str): The category of the message.
        """
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
        self.__content = content

    def format_to_send_with_error_message(self) -> str:
        """
        Format the message to send with an error message.

        Returns:
            str: The formatted message string.
        """
        return f"{self.__category}{HEADER_SEPARATOR_CHAR}{self.__content}"
