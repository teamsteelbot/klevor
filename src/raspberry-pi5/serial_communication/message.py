class Message:
    """
    Class to handle the messages sent and received from the Raspberry Pi Pico.
    """
    # Types of messages
    TYPE_CAPTURE_IMAGE = 'capture_image'
    TYPE_INFERENCE = 'inference'
    TYPE_RPLIDAR_MEASURES = "rplidar_measures"
    TYPES = [TYPE_INFERENCE, TYPE_CAPTURE_IMAGE, TYPE_RPLIDAR_MEASURES]

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
        # Check if the message type is valid
        if message_type not in self.TYPES:
            raise ValueError(f"Invalid message type: {message_type}")
        self.__type = message_type

        # Set the message content
        self.__content = message_content

    def __str__(self) -> str:
        """
        String representation of the message.
        """
        return f"{self.__type}{self.HEADER_SEPARATOR}{self.__content}{self.END}"

    def get_type(self) -> str:
        """
        Get the message type.

        Returns:
            str: The type of the message.
        """
        return self.__type

    def get_content(self) -> str:
        """
        Get the message content.

        Returns:
            str: The content of the message.
        """
        return self.__content
