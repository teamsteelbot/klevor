from utils import check_type

class Message:
    """
    A class to represent a server message.
    This class is used to encapsulate the message data that will be sent
    over the WebSocket connection.
    """
    # Tag separator used to separate the tag from the content in the message string
    TAG_SEPARATOR = ":"

    def __init__(self, tag: str, content: str):
        """
        Initialize the Message instance.

        Args:
            tag (str): A tag associated with the message, used for categorization or filtering.
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
    def tag(self) -> str:
        """
        Get the tag of the message.

        Returns:
            str: The tag of the message.
        """
        return self.__tag
        
    @tag.setter
    def tag(self, value: str):
        """
        Set the tag of the message.

        Args:
            value (str): The new tag for the message.
        """
        check_type(value, str)
        self.__tag = value