from abc import ABC, abstractmethod
from typing import TextIO

from .enums import Category
from .message import Message
from ..files import Files


class LoggerABC(ABC):
    """
    Abstract class to handle logging functionality.
    """

    @abstractmethod
    def get_unique_tag(self, tag: str):
        """
        Generate a unique tag for the logger instance.

        Args:
            tag (str): The tag to identify the logger instance.

        Returns:
            str: A unique tag for the logger instance.
        """

    @abstractmethod
    def log(self, content: str, category: Category = Category.INFO) -> None:
        """
        Put a log message in the queue.

        Args:
            content (str): Content of the log message.
            category (Category): Category of the log message.
        """
        pass

    @abstractmethod
    def info(self, content: str) -> None:
        """
        Log an informational message.

        Args:
            content (str): Content of the log message.
        """
        pass

    @abstractmethod
    def error(self, content: str) -> None:
        """
        Log an error message.

        Args:
            content (str): Content of the log message.
        """
        pass

    @abstractmethod
    def warning(self, content: str) -> None:
        """
        Log a warning message.

        Args:
            content (str): Content of the log message.
        """
        pass

    @abstractmethod
    def debug(self, content: str) -> None:
        """
        Log a debug message.

        Args:
            content (str): Content of the log message.
        """
        pass


class WriterABC(ABC):
    """
    Abstract class to handle writing log messages to a file.
    """

    @classmethod
    def _write(cls, file: TextIO, msg: Message) -> None:
        """
        Write a message to the log file.

        Args:
            file (TextIO): The file to write the message to.
            msg (Message): Message to log.
        """
        # Check if the file is open
        if not file:
            print(f"Log file is not open. Must open it first.")
            return

        # Check if the message is an instance of Message
        if not isinstance(msg, Message):
            cls._write(
                file, Message(
                    f"Invalid message type: {type(msg)}. Expected Message.",
                    Category.ERROR
                )
            )
            return

        # Write the message to the log file
        file.write(f"{msg}\n")

        # Ensure immediate write
        file.flush()

    @abstractmethod
    def _write_last_message(self) -> None:
        """
        Write the last message to the log file if available.

        Raises:
            RuntimeError: If the log file is not open.
        """
        pass

    @abstractmethod
    def _start(self) -> None:
        """
        Start the writer.

        Raises:
            RuntimeError: If the writer fails to start.
        """
        pass

    @abstractmethod
    def _stop(self) -> None:
        """
        Stop the writer.
        """
        pass

    @abstractmethod
    def run(self, file_path: str = Files.get_log_file_path()) -> None:
        """
        Main loop for the logger to write messages to the log file.

        Args:
            file_path (str): Path to the log file.
        """
        pass