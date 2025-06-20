class Category:
    """
    Class to represent the enum categories of messages sent and received from the Raspberry Pi Pico.
    """
    CAPTURE_IMAGE = "capture_image"
    INFERENCE = "yolo_inference"
    RPLIDAR = "rplidar"
    DEBUG = "debug"
    STATUS = "status"
    CHALLENGE = "challenge"
    SERVO = "servo"
    MOTOR = "motor"

    @staticmethod
    def from_string(category_str: str) -> 'Category':
        """
        Convert a string to a Category enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            Category: The corresponding Category enum value.
        """
        category_name = category_str.upper()
        if category_name not in [Category.CAPTURE_IMAGE, Category.INFERENCE, Category.RPLIDAR, Category.DEBUG,
                                 Category.STATUS, Category.CHALLENGE, Category.SERVO, Category.MOTOR]:
            raise ValueError(f"Invalid category: {category_str}")
        return Category[category_name]

class Status:
    """
    Class to represent the enum status messages sent and received from the Raspberry Pi Pico.
    """
    START = "start"
    STOP = "stop"
    OK = "ok"

    @staticmethod
    def from_string(status_str: str) -> 'Status':
        """
        Convert a string to a Status enum value.

        Args:
            status_str (str): The string representation of the status.

        Returns:
            Status: The corresponding Status enum value.
        """
        status_name = status_str.upper()
        if status_name not in [Status.START, Status.STOP, Status.OK]:
            raise ValueError(f"Invalid status: {status_str}")
        return Status[status_name]

class Challenge:
    """
    Class to represent the enum challenge messages sent and received from the Raspberry Pi Pico.
    """
    WITH_OBSTACLES = "with_obstacles"
    WITHOUT_OBSTACLES = "without_obstacles"

    @staticmethod
    def from_string(challenge_str: str) -> 'Challenge':
        """
        Convert a string to a Challenge enum value.

        Args:
            challenge_str (str): The string representation of the challenge.

        Returns:
            Challenge: The corresponding Challenge enum value.
        """
        challenge_name = challenge_str.upper()
        if challenge_name not in [Challenge.WITH_OBSTACLES, Challenge.WITHOUT_OBSTACLES]:
            raise ValueError(f"Invalid challenge: {challenge_str}")
        return Challenge[challenge_name]


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
            msg_str (str): The string representation of the message.

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
        category = Category.from_string(parts[0])

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

