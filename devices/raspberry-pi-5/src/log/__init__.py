from threading import Thread
from multiprocessing import Event, RLock, Queue
from typing import Optional, TextIO, final

from .abstracts import LoggerABC
from .message import Message
from .enums import Category
from ..utils import is_instance
from ..files import Files


class Logger(LoggerABC):
    """
    Class to handle logging functionality.
    """

    # Get message from queue timeout
    GET_MESSAGE_FROM_QUEUE_TIMEOUT = 0.01

    def __init__(self):
        """
        Initialize the Logger class.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create the opened event
        self.__opened_event = Event()

        # Create the stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Initialize the messages queue
        self.__messages_queue: Queue[Message]|None = None

        # Initialize the write log event
        self.__write_log_event = Event()

        # Initialize the thread
        self.__thread = None

    @final
    def log(self, content: str, category: Category = Category.INFO, tag: Optional[str] = None) -> None:
        with self.__rlock:
            # Check the type of content
            is_instance(content, str)

            # Check the type of category
            is_instance(category, Category)

            # Check the type of tag
            is_instance(tag, str) if tag else None

            # Create a message object
            msg = Message(content, category, tag)

            # Check if the logger has stopped
            if self.is_stopped():
                # Write the message to the latest log file
                if not self.__file_path:
                    print("Log file path is not set. Must create thread first.")
                    return
                
                with open(self.__file_path, 'a') as file:
                    self._write(file, msg)
                return

            # If the opened event is not set, wait for it to be set
            if not self.__opened_event.is_set():
                self.__opened_event.wait()

            # Put the message in the queue
            self.__messages_queue.put(msg)

            # Set the write log event
            self.__write_log_event.set()

    @final
    def info(self, content: str, tag: Optional[str] = None) -> None:
        self.log(content, Category.INFO, tag)

    @final
    def error(self, content: str, tag: Optional[str] = None) -> None:
        self.log(content, Category.ERROR, tag)

    @final
    def warning(self, content: str, tag: Optional[str] = None) -> None:
        self.log(content, Category.WARNING, tag)

    @final
    def debug(self, content: str, tag: Optional[str] = None) -> None:
        self.log(content, Category.DEBUG, tag)

    @final
    def _get_message(self) -> Message|None:
        # Get the message from the queue
        with self.__rlock:
            if self.__messages_queue.empty():
                return None
            
            # Return the message from the queue
            return self.__messages_queue.get(timeout=self.GET_MESSAGE_FROM_QUEUE_TIMEOUT)

    @final
    def _write_last_message(self, file: TextIO) -> None:
        # Get the last message from the queue
        msg = self._get_message()

        # Log the message
        self._write(file, msg)

    def __loop(self, file_path: str = Files.get_log_file_path()) -> None:
        """
        Main loop for the logger to write messages to the log file.

        Args:
            file_path (str): Path to the log file.
        """
        # Initialize the messages queue
        self.__messages_queue = Queue()

        # Check the type of file_path
        is_instance(file_path, str)
        self.__file_path = file_path

        # Ensure the file exists
        Files.ensure_file_exists(self.__file_path)

        # Open the log file in append mode
        with open(self.__file_path, 'a') as file:
            # Set the opened event
            self.__opened_event.set()
            self.debug(f"Logger opened at {self.__file_path}.")

            while self.is_running():
                # Wait for the write log event to be set
                self.__write_log_event.wait()

                # Check if the stop event is set
                if self.is_stopped():
                    # Process any remaining messages in the queue
                    while not self.__messages_queue.empty():
                        # Write the last message to the log file
                        self._write_last_message(file)
                    break

                # Write the last message to the log file
                self._write_last_message(file)

                # If the queue is empty, clear the write log event
                if self.__messages_queue.empty():
                    self.__write_log_event.clear()

        # Close queue
        self.__messages_queue.close()

    def __start(self) -> None:
        """
        Set the stop event to allow logging to start.
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

            # Clear the write log event
            self.__write_log_event.clear()

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self) -> None:
        """
        Set the stop event to stop logging messages.
        """
        with self.__rlock:
            # Log the closing message
            self.debug("Logger is closing.")

            # Set the stop event
            self.__stop_event.set()

            # Clear the opened event
            self.__opened_event.clear()

            # Set the write log event
            self.__write_log_event.set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    @final
    def create_thread(self) -> None:
        with self.__rlock:
            # Check if the logger has already started
            if self.is_running():
                self.warning("Logger is already running. Cannot start again.")
                return

            # Start the logger
            self.__start()

            # Create a thread for the logger
            self.__thread = Thread(target=self.__loop)
            self.__thread.start()

    @final
    def stop_thread(self) -> None:
        with self.__rlock:
            # Check if the logger has already stopped
            if self.is_stopped():
                print("Logger is already stopped. Cannot stop again.")
                return

            # Stop the logger
            self.__stop()

            # Set thread to None if it exists
            self.__thread.join()
            self.__thread = None

    def __del__(self):
        """
        Destructor to ensure the logger thread is stopped when the object is deleted.
        """
        self.stop_thread() if self.__thread else None
        print("Logger thread stopped and resources cleaned up.")