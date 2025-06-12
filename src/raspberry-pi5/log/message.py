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
        self.content = content
        self.tag = tag

    def __str__(self):
        """
        String representation of the log message.

        Returns:
            str: The formatted log message.
        """
        return f"[{self.__tag}] {self.__content}" if self.__tag else self.__content

    @property
    def content(self) -> str:
        """
        Get the content of the log message.

        Returns:
            str: The content of the log message.
        """
        return self.__content


    @content.setter
    def content(self, value: str):
        """
        Set the content of the log message.

        Args:
            value (str): The new content for the log message.
        """
        check_type(value, str)
        self.__content = value

    @property
    def tag(self) -> Optional[str]:
        """
        Get the tag of the log message.

        Returns:
            Optional[str]: The tag of the log message, or None if not set.
        """
        return self.__tag

    @tag.setter
    def tag(self, value: Optional[str]):
        """
        Set the tag of the log message.

        Args:
            value (Optional[str]): The new tag for the log message.
        """
        if value is not None:
            check_type(value, str)
        self.__tag = value