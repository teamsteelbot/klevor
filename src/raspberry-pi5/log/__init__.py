from threading import Thread
from multiprocessing import Event, Lock, Queue
from multiprocessing.synchronize import Event as EventCls
from io import TextIOWrapper
from datetime import datetime

from log.message import Message
from utils import check_type
from files import Files


class Logger:
    """
    Class to handle logging functionality.
    """

    def __init__(self, stop_event: EventCls):
        """
        Initialize the Logger class.

        Args:
            stop_event (Event): Event to signal when to stop logging.
        """
        # Check the type of stop_event
        check_type(stop_event, EventCls)
        self.__stop_event = stop_event

        # Initialize the lock
        self.__lock = Lock()

        # Initialize the messages queue
        self.__messages_queue = Queue()

        # Initialize the write log event
        self.__write_log_event = Event()

        # Initialize the thread stop event
        self.__thread_stop_event = None

        # Set the opened flag 
        self.__opened = False

        # Set the thread flag
        self.__thread_started = False

    def log(self, message: Message) -> None:
        """
        Put a log message in the queue.

        Args:
            message (Message): Message to put in the queue.
        """
        with self.__lock:
            # Check the type of message
            check_type(message, Message)

            # Put the message in the queue
            self.__messages_queue.put(str(message))

            # Set the write log event
            self.__write_log_event.set()

    def __get_message(self) -> str|None:
        """
        Get a message from the queue.

        Returns:
            str|None: Message from the queue.
        """
        # Get the message from the queue
        with self.__lock:
            if self.__messages_queue.empty():
                return None
            
            # Return the message from the queue
            return self.__messages_queue.get()
        
    def __write(self, file: TextIOWrapper, message: str) -> None:
        """
        Write a message to the log file.

        Args:
            file (TextIOWrapper): The file to write the message to.
            message (str): Message to log.
        """
        # Get the formatted time
        formatted_time = datetime.now().strftime('%H:%M:%S')

        # Check if the file is open
        if not file:
            print(f"Log file is not open. Must open it first.")
            return

        # Write the message to the log file
        file.write(f"{formatted_time}: {message}\n") 
        
        # Ensure immediate write
        file.flush() 

    def __write_last_message(self, file: TextIOWrapper) -> None:
        """
        Write the last message to the log file.

        Args:
            file (TextIOWrapper): The file to write the message to.
        """
        # Get the last message from the queue
        message = self.__get_message()

        # Log the message
        self.__write(file, message)

    def __open(self) -> None:
        """
        Open the log file.
        """
        with self.__lock:
            if self.__opened:
                return

            # Set the opened flag to True
            self.__opened = True

    def __close(self) -> None:
        """
        Close the log file.
        """
        with self.__lock:
            if not self.__opened:
                return

            # Set the opened flag to False
            self.__opened = False

    def __loop(self, file_path: str = Files.get_log_file_path()) -> None:
        """
        Main loop for the logger to write messages to the log file.

        Args:
            file_path (str): Path to the log file.
        """
        if self.__thread_started:
            return
        
        # Set the thread started flag
        self.__thread_started = True
        
        # Open the log file
        self.__open()

        # Check the type of file_path
        check_type(file_path, str)
        self.__file_path = file_path

        # Ensure the file path exists
        Files.ensure_path_exists(self.__file_path)

        # Open the log file in append mode
        try:
            with open(self.__file_path, 'a') as file:
                while not self.__stop_event.is_set():
                    # Wait for the write log event to be set
                    self.__write_log_event.wait()

                    # Check if the thread stop event is set
                    if self.__thread_stop_event and self.__thread_stop_event.is_set():
                        break

                    # Write the last message to the log file
                    self.__write_last_message(file)

                    if self.__messages_queue.empty():
                        # If the queue is empty, clear the write log event
                        self.__write_log_event.clear()
                        continue
        
        finally:
            self.__close()
            self.__thread_started = False

    def get_stop_event(self) -> EventCls:
        """
        Get the stop event status.

        Returns:
            Event: The stop event.
        """
        return self.__stop_event
    
    def create_thread(self) -> None:
        """
        Create thread for the logger.
        """
        with self.__lock:
            # Create a thread for the logger
            thread = Thread(target=self.__loop)
            thread.start()

            # Create the thread stop event
            self.__thread_stop_event = Event() 

    def stop_thread(self) -> None:
        """
        Stop the logger thread.
        """
        with self.__lock:
            if self.__thread_stop_event:
                # Set the write log event to ensure the thread stops
                self.__write_log_event.set()

                # Set the thread stop event
                self.__thread_stop_event.set()
                
                # Clear the write log event
                self.__write_log_event.clear()

                # Set the thread stop event to None
                self.__thread_stop_event = None

    def __del__(self):
        """
        Destructor to close the log file if it is open.
        """
        if self.__thread_started:
            self.stop_thread()
        else:
            self.__close()
