from queue import Empty
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from typing import TextIO, final

from .abstracts import WriterABC
from .enums import Category
from .message import Message
from ..files import Files
from ..utils import is_instance
from ..utils.decorators import ignore_sigint


class Writer(WriterABC):
    """
    Class to handle writing log messages to a file.
    """

    # Wait timeout for processing messages
    WAIT_TIMEOUT = 0.1

    def __init__(self, messages_queue: Queue, stop_event: EventCls) -> None:
        """
        Initialize the Logger class.

        Args:
            messages_queue (Queue): Queue to hold log messages.
            stop_event (EventCls): Event to signal when the logger should stop.
        """
        # Initialize the messages queue and events
        self.__messages_queue = messages_queue
        self.__opened_event = Event()
        self.__stop_event = stop_event

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the file path and file
        self.__file_path: str = ""
        self.__file: TextIO | None = None

    @final
    def _write_last_message(self) -> None:
        try:
            # Process any remaining messages in the queue
            msg = self.__messages_queue.get(timeout=self.WAIT_TIMEOUT)

            # Write the message to the log file
            self._write(self.__file, msg)

        except Empty:
            # If the queue is empty, do nothing
            return None

    @final
    @ignore_sigint
    def run(self, file_path: str = Files.get_log_file_path()) -> None:
        try:
            with self.__rlock:
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
                with self.__rlock:
                    self.__opened_event.set()

                # Write the initial message to the log file
                self._write(
                    self.__file,
                    Message(
                        f"Log file opened at {self.__file_path}.",
                        Category.DEBUG
                    )
                )

                # Main loop to write messages to the log file
                self._write(
                    self.__file,
                    Message("Writer's starting...", Category.DEBUG)
                )
                while not self.__stop_event.is_set():
                    # Write the last message if available
                    self._write_last_message()

                # Check if there are any remaining messages in the queue
                while not self.__messages_queue.empty():
                    # Write the last message if available
                    self._write_last_message()

                # Write the stop message to the log file
                self._write(self.__file, Message("Writer stopped.", Category.DEBUG))

        except Exception as e:
            # Log any exceptions that occur
            print(f"An error occurred: {e}")
            self._write(self.__file, Message(f"Error: {e}", Category.ERROR))

        # Clear the opened event
        with self.__rlock:
            self.__opened_event.clear()

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return self.__opened_event.is_set() and not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the photographer is no longer needed.
        """
        self.__stop_event.set()

        # Log
        print("Writer instance is being deleted. Resources will be cleaned up.")
