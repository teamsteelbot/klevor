from . import Logger
from .message import Category
from ..utils import check_type


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
        self.logger = logger
        self.tag = tag

    @property
    def tag(self) -> str:
        """
        Get the tag of the logger.

        Returns:
            str: The tag used for logging.
        """
        return self.__tag

    @tag.setter
    def tag(self, tag: str) -> None:
        """
        Set the tag for the logger.

        Args:
            tag (str): New tag for the log messages.
        """
        # Check the type of tag
        check_type(tag, str)
        self.__tag = tag

    @property
    def logger(self) -> Logger:
        """
        Get the logger instance.

        Returns:
            Logger: The logger instance used for logging.
        """
        return self.__logger

    @logger.setter
    def logger(self, logger: Logger) -> None:
        """
        Set the logger instance.

        Args:
            logger (Logger): New logger instance to use for logging.
        """
        # Check the type of logger
        check_type(logger, Logger)
        self.__logger = logger

    def log(self, content: str, category: Category = Category.INFO) -> None:
        """
        Log a message with the specified tag.

        Args:
            content (str): Content of the log message.
            category (Category): Category of the log message.
        """
        self.logger.log(content, category, self.tag)

    def info(self, content: str) -> None:
        """
        Log an info message.

        Args:
            content (str): Content of the info message.
        """
        self.logger.info(content, self.tag)

    def warning(self, content: str) -> None:
        """
        Log a warning message.

        Args:
            content (str): Content of the warning message.
        """
        self.logger.warning(content, self.tag)

    def error(self, content: str) -> None:
        """
        Log an error message.

        Args:
            content (str): Content of the error message.
        """
        self.logger.error(content, self.tag)

    def debug(self, content: str) -> None:
        """
        Log a debug message.

        Args:
            content (str): Content of the debug message.
        """
        self.logger.debug(content, self.tag)