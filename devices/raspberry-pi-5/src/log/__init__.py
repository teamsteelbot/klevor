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

    def __init__(self, messages_queue: Queue, opened_event: Event, tag: Optional[str] = None):
        """
        Initialize the Logger class.

        Args:
            messages_queue (Queue): Queue to hold log messages.
            opened_event (Event): Event to signal when the logger is ready to write messages.
            tag (Optional[str]): Tag to identify the logger instance.
        """
        # Initialize the messages queue and events
        self.__messages_queue = messages_queue
        self.__opened_event = opened_event

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

        # Check if the opened event is set
        if not self.__opened_event.is_set():
            # If the opened event is not set, wait for it to be set
            self.__opened_event.wait()

        # Put the message in the queue
        self.__messages_queue.put(msg)

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