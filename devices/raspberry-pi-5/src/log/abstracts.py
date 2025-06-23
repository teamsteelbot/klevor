from multiprocessing import Queue, Event
from abc import ABC, abstractmethod
from typing import TextIO

from .message import Message
from .enums import Category
from ..files import Files

class LoggerABC(ABC):
    """
    Abstract class to handle logging functionality.
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

    @staticmethod
    def _write(file: TextIO, message: Message) -> None:
        """
        Write a message to the log file.

        Args:
            file (TextIO): The file to write the message to.
            message (Message): Message to log.
        """
        # Check if the file is open
        if not file:
            print(f"Log file is not open. Must open it first.")
            return

        if not message:
            print("No message to log.")
            return

        # Write the message to the log file
        file.write(f"{message}\n")

        # Ensure immediate write
        file.flush()

    @abstractmethod
    def _get_message(self) -> Message | None:
        """
        Get a message from the queue.

        Returns:
            Message|None: Message from the queue.
        """
        pass

    @abstractmethod
    def _write_last_message(self) -> None:
        """
        Write the last message to the log file.
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

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the stop event is not set, indicating that's allowed to log messages.

        Returns:
            bool: True if the stop event is not set, False otherwise.
        """
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        """
        Check if the logger is stopped by checking if the stop event is set.

        Returns:
            bool: True if the stop event is set (indicating the logger is stopped), False otherwise.
        """
        pass