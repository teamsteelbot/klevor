from utils import check_type


class Message:
    """
    Class to handle log messages.
    """

    def __init__(self, tag: str, content: str):
        """
        Initialize the Message class.

        Args:
            tag (str): Tag of the log message.
            content (str): Content of the log message.
        """
        # Check the type of ta
        check_type(tag, str)
        self.__tag = tag

        # Check the type of content
        check_type(content, str)
        self.__content = content

    def __str__(self):
        """
        String representation of the log message.

        Returns:
            str: The formatted log message.
        """
        return f"[{self.__tag}] {self.__content}"
