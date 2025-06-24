from multiprocessing import Queue
from typing import Optional, final

from .abstracts import LoggerABC
from .enums import Category
from .message import Message
from ..utils import is_instance


class Logger(LoggerABC):
    """
    Class to handle logging functionality.
    """

    def __init__(
        self,
        writer_messages_queue: Queue,
        tag: Optional[str] = None,
        unique_tag: bool = False
    ) -> None:
        """
        Initialize the Logger class.

        Args:
            writer_messages_queue (Queue): Queue to hold log messages.
            tag (Optional[str]): Tag to identify the logger instance.
            unique_tag (bool): Whether to generate a unique tag for the logger instance.
        """
        # Initialize the messages queue and events
        self.__writer_messages_queue = writer_messages_queue

        # Check the type of tag
        is_instance(tag, (str, None,))
        self.__tag = self.get_unique_tag(tag) if unique_tag or not tag else tag

        # Log the initialization if a tag is provided
        self.debug(
            f"Initializing Logger with tag: {self.__tag}"
        ) if self.__tag else None

    @final
    def get_unique_tag(self, tag: str):
        return f"{tag}_{id(self)}" if tag else f"Logger_{id(self)}"

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
