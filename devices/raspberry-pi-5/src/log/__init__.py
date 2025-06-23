from multiprocessing import Event, Queue
from typing import final, Optional

from .abstracts import LoggerABC
from .message import Message
from .enums import Category
from ..utils import is_instance


class Logger(LoggerABC):
    """
    Class to handle logging functionality.
    """

    def __init__(self, writer_messages_queue: Queue, tag: Optional[str] = None):
        """
        Initialize the Logger class.

        Args:
            writer_messages_queue (Queue): Queue to hold log messages.
            tag (Optional[str]): Tag to identify the logger instance.
        """
        # Initialize the messages queue and events
        self.__writer_messages_queue = writer_messages_queue

        # Check the type of tag
        if tag is not None:
            is_instance(tag, str)
        self.__tag = tag

    @final
    def log(self, content: str, category: Category = Category.INFO) -> None:
        # Check the type of content
        is_instance(content, str)

        # Check the type of category
        is_instance(category, Category)

        # Create a message object
        msg = Message(content, category, self.__tag)

        # Put the message in the queue
        self.__writer_messages_queue.put(msg)

    @final
    def info(self, content: str) -> None:
        self.log(content, Category.INFO)

    @final
    def error(self, content: str) -> None:
        self.log(content, Category.ERROR)

    @final
    def warning(self, content: str) -> None:
        self.log(content, Category.WARNING)

    @final
    def debug(self, content: str) -> None:
        self.log(content, Category.DEBUG)