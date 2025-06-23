from multiprocessing import Event, Queue
from typing import TextIO, final

from .abstracts import WriterABC
from .enums import Category
from .message import Message
from ..files import Files
from ..utils import is_instance


class Writer(WriterABC):
    """
    Class to handle writing log messages to a file.
    """

    # Wait timeout for processing messages
    WAIT_TIMEOUT = 0.1

    def __init__(self, messages_queue: Queue, opened_event: Event,
                 stop_event: Event):
        """
        Initialize the Logger class.

        Args:
            messages_queue (Queue): Queue to hold log messages.
            opened_event (Event): Event to signal when the logger is ready to write messages.
            stop_event (Event): Event to signal when the logger should stop.
        """
        # Initialize the messages queue and events
        self.__messages_queue = messages_queue
        self.__opened_event = opened_event
        self.__opened_event.clear()
        self.__stop_event = stop_event

        # Initialize the file path and file
        self.__file_path: str = ""
        self.__file: TextIO | None = None

        # Initialize the thread
        self.__thread = None

    @final
    def _write_last_message(self) -> None:
        # Process any remaining messages in the queue
        msg = self.__messages_queue.get(timeout=self.WAIT_TIMEOUT)
        if msg is None:
            return None

        # Write the message to the log file
        self._write(self.__file, msg)

    def run(self, file_path: str = Files.get_log_file_path()) -> None:
        """
        Main loop for the logger to write messages to the log file.

        Args:
            file_path (str): Path to the log file.
        """
        # Check if the stop event is set
        if self.__stop_event.is_set():
            print("Stop event is set. Logger will not run.")
            return

        # Check if the logger is already running
        if self.is_running():
            print("Logger is already running. Cannot start again.")
            return

        # Check the type of file_path
        is_instance(file_path, str)
        self.__file_path = file_path

        # Ensure the file exists
        Files.ensure_file_exists(self.__file_path)

        # Open the log file in append mode
        print(f"Opening log file at {self.__file_path}...")
        with open(self.__file_path, 'a') as file:
            # Set the file
            self.__file = file

            # Set the opened event
            self.__opened_event.set()

            # Write the initial message to the log file
            self._write(self.__file,
                        Message(f"Log file opened at {self.__file_path}.",
                                Category.DEBUG))

            # Main loop to write messages to the log file
            self._write(self.__file,
                        Message("Writer's starting...", Category.DEBUG))
            while not self.__stop_event.is_set():
                # Write the last message if available
                self._write_last_message()

            # Check if there are any remaining messages in the queue
            while not self.__messages_queue.empty():
                # Write the last message if available
                self._write_last_message()

            # Write the stop message to the log file
            self._write(self.__file, Message("Writer stopped.", Category.DEBUG))

        # Clear the opened event
        self.__opened_event.clear()

    @final
    def is_running(self) -> bool:
        return self.__opened_event.is_set() and not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the photographer is no longer needed.
        """
        self.__stop_event.set()
