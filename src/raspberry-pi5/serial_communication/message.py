from utils import check_type

class Message:
    """
    Class to handle the messages sent and received from the Raspberry Pi Pico.
    """
    # Types of messages
    TYPE_CAPTURE_IMAGE = 'capture_image'
    TYPE_INFERENCE = 'inference'
    TYPE_RPLIDAR_MEASURES = "rplidar_measures"
    TYPE_DEBUG = 'debug'
    TYPE_STATUS = 'status'
    TYPES = [TYPE_INFERENCE, TYPE_CAPTURE_IMAGE, TYPE_RPLIDAR_MEASURES, TYPE_DEBUG, TYPE_STATUS]

    # Types of Status
    TYPE_STATUS_ON = 'on'
    TYPE_STATUS_OFF = 'off'

    # Message header separator
    HEADER_SEPARATOR = ':'

    # Message end character
    END = '\n'

    def __init__(self, message_type: str, message_content: str):
        """
        Initialize the message class.

        Args:
            message_type (str): The type of the message. Must be one of TYPES.
            message_content (str): The content of the message.
        """
        # Set the message type
        self.type = message_type

        # Set the message content
        self.content = message_content

    def __str__(self) -> str:
        """
        String representation of the message.
        """
        return f"{self.__type}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

    @property
    def type(self) -> str:
        """
        Property to get the message type.

        Returns:
            str: The type of the message.
        """
        return self.__type

    @type.setter
    def type(self, message_type: str):
        """
        Setter for the message type.

        Args:
            message_type (str): The type of the message. Must be one of TYPES.
        """
        # Check the type of message
        check_type(message_type, str)

        # Check if the message type is valid
        if message_type not in self.TYPES:
            raise ValueError(f"Invalid message type: {message_type}")
        self.__type = message_type

    @property
    def content(self) -> str:
        """
        Get the message content.

        Returns:
            str: The content of the message.
        """
        return self.__content

    @content.setter
    def content(self, message_content: str):
        """
        Setter for the message content.

        Args:
            message_content (str): The content of the message.
        """
        # Check the type of content
        check_type(message_content, str)
        self.__content = message_content