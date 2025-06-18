from typing import final

from .abstracts import LoggerABC, SubLoggerABC
from ..utils import check_type


class SubLogger(SubLoggerABC):
    """
    Class to handle sub-logging functionality.
    """

    def __init__(self, logger: LoggerABC, tag: str):
        """
        Initialize the SubLogger class.

        Args:
            logger (LoggerABC): Logger instance to use for logging.
            tag (str): Tag for the log messages.
        """
        self.logger = logger
        self.tag = tag

    @final
    @property
    def tag(self) -> str:
        return self.__tag

    @final
    @tag.setter
    def tag(self, tag: str) -> None:
        # Check the type of tag
        check_type(tag, str)
        self.__tag = tag

    @final
    @property
    def logger(self) -> LoggerABC:
        return self.__logger

    @final
    @logger.setter
    def logger(self, logger: LoggerABC) -> None:
        # Check the type of logger
        check_type(logger, LoggerABC)
        self.__logger = logger