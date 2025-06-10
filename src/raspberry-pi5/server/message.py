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
        # Check the type of content
        check_type(content, str)
        self.__content = content

        # Check the type of tag
        check_type(tag, str)
        self.__tag = tag

    
    def __str__(self):
        """
        Return a string representation of the Message instance.
        This is useful for logging or debugging purposes.
        """
        return f"{self.__tag}{self.TAG_SEPARATOR}{self.__content}"
        

