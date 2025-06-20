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

    @staticmethod
    def from_string(tag_str: str) -> "Tag":
        """
        Convert a string to a Tag enum value.

        Args:
            tag_str (str): The string representation of the tag.

        Returns:
            Tag: The corresponding Tag enum value.
        """
        tag_name = tag_str.upper()
        if tag_name not in Tag.__members__:
            raise ValueError(f"Invalid tag: {tag_str}")
        return Tag[tag_name]


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
    
    @staticmethod
    def from_string(msg_str: str) -> "Message":
        """
        Create a Message instance from a string representation.

        Args:
            msg_str (str): The string representation of the message.

        Returns:
            Message: A new Message instance created from the string.
        """
        # Split the string into category and content
        parts = msg_str.strip().split(Message.TAG_SEPARATOR, 1)
        if len(parts) != 2:
            raise ValueError("Invalid message format")

        # Convert the tag string to a Tag enum value
        tag = Tag.from_string(parts[0])

        # Create and return the Message object
        return Message(tag, parts[1])

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