class IncomingCategory:
    """
    Class to represent the enum categories of incoming messages from the Raspberry Pi 5.
    """
    STATUS = "status"
    MOTOR_SPEED = "motor_speed"
    SERVO_ANGLE = "servo_angle"

    @classmethod
    def from_string(cls, category_str: str) -> str:
        """
        Convert a string to a IncomingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            str: The corresponding IncomingCategory enum value.
        """
        category_name = category_str.upper()
        for category in [cls.STATUS, cls.MOTOR_SPEED, cls.SERVO_ANGLE]:
            if category_name == category:
                return category

        raise ValueError(f"Invalid incoming category: {category_str}")

class OutgoingCategory:
    """
    Class to represent the enum categories of outgoing messages to the Raspberry Pi 5.
    """
    CHALLENGE = "challenge"
    STATUS = "status"
    BNO08X_YAW = "bno08x_yaw"
    BNO08X_TURNS = "bno08x_turns"
    ERROR = "error"

    @classmethod
    def from_string(cls, category_str: str) -> str:
        """
        Convert a string to a OutgoingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            str: The corresponding OutgoingCategory enum value.
        """
        category_name = category_str.upper()
        for category in [cls.CHALLENGE, cls.STATUS, cls.BNO08X_YAW,
                         cls.BNO08X_TURNS, cls.ERROR]:
            if category_name == category:
                return category

        raise ValueError(f"Invalid outgoing category: {category_str}")

class Status:
    """
    Class to represent the enum status messages sent and received to the Raspberry Pi 5.
    """
    START = "start"
    STOP = "stop"
    OK = "ok"

    @classmethod
    def from_string(cls, status_str: str) -> str:
        """
        Convert a string to a Status enum value.

        Args:
            status_str (str): The string representation of the status.

        Returns:
            str: The corresponding Status enum value.
        """
        status_name = status_str.upper()
        for status in [cls.START, cls.STOP, cls.OK]:
            if status_name == status:
                return status

        raise ValueError(f"Invalid status: {status_str}")

class Request:
    """
    Class to represent the enum request messages sent to the Raspberry Pi 5.
    """

    INFERENCE = "inference"

    @classmethod
    def from_string(cls, request_str: str) -> str:
        """
        Convert a string to a Request enum value.

        Args:
            request_str (str): The string representation of the request.

        Returns:
            str: The corresponding Request enum value.
        """
        request_name = request_str.upper()
        for request in [cls.INFERENCE]:
            if request_name == request:
                return request

        raise ValueError(f"Invalid request: {request_str}")

class IncomingMessage:
    """
    Class to handle the messages received from the Raspberry Pi 5.
    """
    # Message header separator
    HEADER_SEPARATOR = ':'

    # Content header separator
    CONTENT_HEADER_SEPARATOR = '='

    # Content separator
    CONTENT_SEPARATOR = ','

    # Message end character
    END = '\n'

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
        return f"{self.__category}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

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
        if msg_str.endswith(IncomingMessage.END):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(IncomingMessage.HEADER_SEPARATOR, 1)
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
    # Message header separator
    HEADER_SEPARATOR = ':'

    # Message end character
    END = '\n'

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
        return f"{self.__category}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

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
        if msg_str.endswith(OutgoingMessage.END):
            msg_str = msg_str[:-1]

        # Split the string into category and content
        parts = msg_str.strip().split(OutgoingMessage.HEADER_SEPARATOR, 1)
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