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
        self.tag = tag
        self.messages_queue = messages_queue
        self.opened_event = opened_event

    @final
    @property
    def tag(self) -> str:
        return self.__tag

    @final
    @tag.setter
    def tag(self, tag: Optional[str]) -> None:
        # Check the type of tag
        if tag is None:
            self.__tag = None
            return

        is_instance(tag, str)
        self.__tag = tag

    @final
    @property
    def messages_queue(self) -> Queue:
        return self.__messages_queue

    @final
    @messages_queue.setter
    def messages_queue(self, messages_queue: Queue) -> None:
        self.__messages_queue = messages_queue

    @final
    @property
    def opened_event(self) -> Event:
        return self.__opened_event

    @final
    @opened_event.setter
    def opened_event(self, opened_event: Event) -> None:
        self.__opened_event = opened_event

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