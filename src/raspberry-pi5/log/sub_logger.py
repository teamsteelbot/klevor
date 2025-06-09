from log import Logger
from log.message import Message
from utils import check_type


class SubLogger:
    """
    Class to handle sub-logging functionality.
    """

    def __init__(self, logger: Logger, tag: str):
        """
        Initialize the SubLogger class.

        Args:
            logger (Logger): Logger instance to use for logging.
            tag (str): Tag for the log messages.
        """
        # Check the type of logger
        check_type(logger, Logger)
        self.__logger = logger

        # Check the type of tag
        check_type(tag, str)
        self.__tag = tag

    def log(self, content: str) -> None:
        """
        Log a message with the specified tag.

        Args:
            content (str): Content of the log message.
        """
        # Check the type of content
        check_type(content, str)

        # Create a Message instance and put it in the logger's message queue
        self.__logger.log(Message(content, self.__tag))
