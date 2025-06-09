from utils import check_type
from typing import Optional

class Message:
    """
    Class to handle log messages.
    """

    def __init__(self, content: str, tag: Optional[str] = None):
        """
        Initialize the Message class.

        Args:
            tag (str): Tag of the log message.
            content (str): Content of the log message.
        """
        # Check the type of content
        check_type(content, str)
        self.__content = content

        # Check the type of tag
        if tag:
            check_type(tag, str)
        self.__tag = tag

    def __str__(self):
        """
        String representation of the log message.

        Returns:
            str: The formatted log message.
        """
        return f"[{self.__tag}] {self.__content}" if self.__tag else self.__content
