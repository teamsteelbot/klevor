from enum import Enum, unique

from ..utils import check_type

@unique
class Tag(Enum):
    """
    Enum to represent the tags of messages sent and received from the server.
    This is used for categorizing or filtering messages based on their type.
    """
    CONNECTION_STATUS = 1
    SERIAL_INCOMING_MESSAGE = 2
    SERIAL_OUTGOING_MESSAGE = 3
    IMAGE_ORIGINAL = 4
    IMAGE_MODEL_G = 5
    IMAGE_MODEL_M = 6
    IMAGE_MODEL_R = 7
    RPLIDAR_MEASURES = 8
    STOP_EVENT = 9
    PARKING_EVENT = 10


class Message:
    """
    A class to represent a server message.
    This class is used to encapsulate the message data that will be sent
    over the WebSocket connection.
    """
    # Tag separator used to separate the tag from the content in the message string
    TAG_SEPARATOR = ":"

    def __init__(self, tag: Tag, content: str):
        """
        Initialize the Message instance.

        Args:
            tag (Tag): A tag associated with the message, used for categorization or filtering.
            content (str): The content of the message.
        """
        self.content = content
        self.tag = tag
    
    def __str__(self):
        """
        Return a string representation of the Message instance.
        This is useful for logging or debugging purposes.
        """
        return f"{self.__tag}{self.TAG_SEPARATOR}{self.__content}"

    @property
    def content(self) -> str:
        """
        Get the content of the message.

        Returns:
            str: The content of the message.
        """
        return self.__content

    @content.setter
    def content(self, value: str):
        """
        Set the content of the message.

        Args:
            value (str): The new content for the message.
        """
        check_type(value, str)
        self.__content = value

    @property
    def tag(self) -> Tag:
        """
        Get the tag of the message.

        Returns:
            Tag: The tag of the message.
        """
        return self.__tag
        
    @tag.setter
    def tag(self, value: Tag):
        """
        Set the tag of the message.

        Args:
            value (Tag): The new tag for the message.
        """
        check_type(value, Tag)
        self.__tag = value