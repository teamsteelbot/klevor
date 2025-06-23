from multiprocessing import RLock, Event, Queue
from threading import Thread
from time import sleep
from typing import TextIO, final

from ..files import Files
from ..utils import is_instance
from .abstracts import WriterABC
from .message import Message
from .enums import Category

class Writer(WriterABC):
    """
    Class to handle writing log messages to a file.
    """

    # Delay for writing messages to the log file
    WRITE_LOG_DELAY = 0.1

    def __init__(self, messages_queue: Queue, opened_event: Event, stop_event: Event):
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

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the file
        self.__file: TextIO | None = None

        # Initialize the thread
        self.__thread = None

    @final
    @property
    def opened_event(self) -> Event:
        return self.__opened_event

    @final
    @property
    def messages_queue(self) -> Queue:
        return self.__messages_queue

    @final
    @property
    def stop_event(self) -> Event:
        return self.__stop_event

    @final
    def _get_message(self) -> Message | None:
        # Get the message from the queue
        with self.__rlock:
            if self.__messages_queue.empty():
                return None

            # Return the message from the queue
            return self.__messages_queue.get()

    @final
    def _write_last_message(self) -> None:
        # Get the last message from the queue
        msg = self._get_message()

        # Log the message
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
            self._write(self.__file, Message(f"Logger opened at {self.__file_path}.", Category.DEBUG))

            while not self.stop_event.is_set():
                # Process any remaining messages in the queue
                while not self.__messages_queue.empty():
                    # Write the last message to the log file
                    self._write_last_message()

                # Sleep for a short duration to avoid busy waiting
                sleep(self.WRITE_LOG_DELAY)

            # Write the stop message to the log file
            self._write(self.__file, Message("Logger is stopping.", Category.DEBUG))

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
        Destructor to ensure the logger thread is stopped when the object is deleted.
        """
        self.stop_event.set()