class IncomingCategory:
    """
    Class to represent the enum categories of incoming messages from the Raspberry Pi 5.
    """
    STATUS = "status"
    INFERENCE = "inference"
    RPLIDAR = "rplidar"

    @classmethod
    def from_string(cls, category_str: str) -> 'IncomingCategory':
        """
        Convert a string to a IncomingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            IncomingCategory: The corresponding IncomingCategory enum value.
        """
        category_name = category_str.upper()
        if category_name not in [cls.STATUS, cls.INFERENCE, cls.RPLIDAR]:
            raise ValueError(f"Invalid incoming category: {category_str}")
        return cls[category_name]

class RPLIDAR:
    """
    Class to represent the enum categories of RPLIDAR messages from the Raspberry Pi 5.
    """
    FRONT = "front"
    LEFT = "left"
    RIGHT = "right"

    @classmethod
    def from_string(cls, category_str: str) -> 'RPLIDAR':
        """
        Convert a string to a RPLIDAR enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            RPLIDAR: The corresponding RPLIDAR enum value.
        """
        category_name = category_str.upper()
        if category_name not in [cls.FRONT, cls.LEFT, cls.RIGHT]:
            raise ValueError(f"Invalid RPLIDAR category: {category_str}")
        return cls[category_name]

class OutgoingCategory:
    """
    Class to represent the enum categories of outgoing messages to the Raspberry Pi 5.
    """
    CHALLENGE = "challenge"
    STATUS = "status"
    SERVO_ANGLE = "servo_angle"
    MOTOR_SPEED = "motor_speed"
    BNO08X_TURNS = "bno08x_turns"
    REQUEST = "request"
    ERROR = "error"

    @classmethod
    def from_string(cls, category_str: str) -> 'OutgoingCategory':
        """
        Convert a string to a OutgoingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            OutgoingCategory: The corresponding OutgoingCategory enum value.
        """
        category_name = category_str.upper()
        if category_name not in [cls.CHALLENGE, cls.STATUS, cls.SERVO_ANGLE, cls.MOTOR_SPEED, cls.REQUEST,
                                 cls.BNO08X_TURNS, cls.ERROR]:
            raise ValueError(f"Invalid outgoing category: {category_str}")
        return cls[category_name]

class Status:
    """
    Class to represent the enum status messages sent and received to the Raspberry Pi 5.
    """
    START = "start"
    STOP = "stop"
    OK = "ok"

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
        if status_name not in [cls.START, cls.STOP, cls.OK]:
            raise ValueError(f"Invalid status: {status_str}")
        return cls[status_name]

class Request:
    """
    Class to represent the enum request messages sent to the Raspberry Pi 5.
    """
    INFERENCE = "inference"

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
        if request_name not in [cls.INFERENCE, cls.RPLIDAR]:
            raise ValueError(f"Invalid request: {request_str}")
        return cls[request_name]

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

    def __init__(self, category: IncomingCategory, content: str):
        """
        Initialize the message class.

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

    def __init__(self, category: OutgoingCategory, content: str):
        """
        Initialize the message class.

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