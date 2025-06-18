from abc import ABC, abstractmethod
from typing import Optional, TextIO

from .message import Category, Message

class LoggerABC(ABC):
    """
    Abstract class to handle logging functionality.
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
    def _write_last_message(self, file: TextIO) -> None:
        """
        Write the last message to the log file.

        Args:
            file (TextIO): The file to write the message to.
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

    @abstractmethod
    def create_thread(self) -> None:
        """
        Create thread for the logger.
        """
        pass

    @abstractmethod
    def stop_thread(self) -> None:
        """
        Stop the logger thread.
        """
        pass

    @abstractmethod
    def log(self, content: str, category: Category = Category.INFO, tag: Optional[str] = None) -> None:
        """
        Put a log message in the queue.

        Args:
            content (str): Content of the log message.
            category (Category): Category of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        pass

    @abstractmethod
    def info(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log an informational message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        pass

    @abstractmethod
    def error(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log an error message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        pass

    @abstractmethod
    def warning(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log a warning message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        pass

    @abstractmethod
    def debug(self, content: str, tag: Optional[str] = None) -> None:
        """
        Log a debug message.

        Args:
            content (str): Content of the log message.
            tag (Optional[str]): Optional tag for the log message.
        """
        pass

class SubLoggerABC(ABC):
    """
    Abstract class to handle sub-logging functionality.
    """

    @property
    @abstractmethod
    def tag(self) -> str:
        """
        Get the tag of the logger.

        Returns:
            str: The tag used for logging.
        """
        pass

    @tag.setter
    @abstractmethod
    def tag(self, tag: str) -> None:
        """
        Set the tag for the logger.

        Args:
            tag (str): New tag for the log messages.
        """
        pass

    @property
    @abstractmethod
    def logger(self) -> LoggerABC:
        """
        Get the logger instance.

        Returns:
            LoggerABC: The logger instance used for logging.
        """
        pass

    @logger.setter
    def logger(self, logger: LoggerABC) -> None:
        """
        Set the logger instance.

        Args:
            logger (LoggerABC): New logger instance to use for logging.
        """
        pass

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
