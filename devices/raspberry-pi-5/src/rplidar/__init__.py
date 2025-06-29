import subprocess
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import Optional, final

from .abstracts import RPLidarABC
from .constants import (
    DISTANCE_DIFF,
    RPLIDAR_C1_BAUDRATE,
    RPLIDAR_C1_PORT,
    ULTRA_SIMPLE_PATH,
    MAX_DISTANCE_LIMIT
)
from ..common.measure import Measure
from ..log import Logger
from ..server.dispatcher import Dispatcher as WebSocketServerDispatcher
from ..utils import is_instance
from ..utils.decorators import ignore_sigint
from ..log.decorators import log_on_error
from ..log.protocols import LoggerConsumerProtocol


class RPLidar(RPLidarABC, LoggerConsumerProtocol):
    """
    Class to handle RPLidar operations.
    """

    # Logger configuration
    LOGGER_TAG = "RPLidar"

    # Process wait timeout
    PROCESS_WAIT_TIMEOUT = 5

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    # Wait timeout for the start event
    START_WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        debug: bool,
        update_measures_event: EventCls,
        measures_queue: Queue,
        start_event: EventCls,
        stop_event: EventCls,
        writer_messages_queue: Queue,
        server_messages_queue: Optional[Queue] = None,
        baudrate: int = RPLIDAR_C1_BAUDRATE,
        port: str = RPLIDAR_C1_PORT,
        is_upside_down: bool = True
    ):
        """
        Initialize the RPLidar.

        Args:
            debug (bool): Flag to indicate if the RPLidar is in debug mode.
            update_measures_event (EventCls): Event to signal when the RPLidar should update measures.
            measures_queue (Queue): Queue to hold the measures from the RPLidar.
            start_event (EventCls): Event to signal when the RPLidar should start.
            stop_event (EventCls): Event to signal when the RPLidar should stop.
            writer_messages_queue (Queue): Queue to hold log messages.
            server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server.
            baudrate (int): Baud rate for the serial communication.
            port (str): SerialCommunication port for the RPLidar.
            is_upside_down (bool): If True, the RPLidar is upside down, and angles will be adjusted accordingly.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the queues and events
        self.__update_measures_event = update_measures_event
        self.__measures_queue = measures_queue
        self.__started_event = Event()
        self.__start_event = start_event
        self.__deleted_event = Event()
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue,
                               tag=self.LOGGER_TAG,
                               debug=self.__debug)

        # Initialize the server dispatcher
        self.__server_dispatcher = WebSocketServerDispatcher(
            server_messages_queue,
            writer_messages_queue
        ) if server_messages_queue else None

        # Create the reentrant lock
        self.__rlock = RLock()

        # Check the type of baudrate
        is_instance(baudrate, int)
        self.__baudrate = baudrate

        # Check the type of the port
        is_instance(port, str)
        self.__port = port

        # Check the type of is_upside_down
        is_instance(is_upside_down, bool)
        self.__is_upside_down = is_upside_down

        # Initialize measures dictionary
        self.__measures = {angle: Measure(angle*1.0, 0.0, 0) for angle in range(361)}

        # Messages counter
        self.__messages_counter = 0

        # Initialize the process
        self.__process = None

        # Initialize the rotation flag
        self.__rotation = False

        # Initialize the listener thread for measures updates
        self.__update_measures_listener_thread = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _read_output(self):
        if not self.__process:
            return

        # Read a line from the process output
        line = self.__process.stdout.readline()
        if not line:
            return

            # Check if it's one of the first 6 messages
        if self.__messages_counter < 6:
            self.__messages_counter += 1
            return

        # Check if the listener thread for measures updates is running
        if not self.__update_measures_listener_thread:
            # Create and start the listener thread
            self.__update_measures_listener_thread = Thread(
                target=self._update_measures_event_listener,
            )
            self.__update_measures_listener_thread.start()

        # Strip the line to remove leading/trailing whitespace
        parsed_line = line.strip()

        # Split the line by spaces
        parts = parsed_line.split()

        # Ignore if there are not enough parts
        if len(parts) < 6:
            return

        # Check if it's the last measure of a full rotation
        rotation = len(parts) == 7
        if rotation:
            parts = parts[1:]

            # Log the end of the rotation
            self.__logger.info("Full rotation completed.")

        # Get the angle, distance and quality
        angle = float(parts[1])
        distance = float(parts[3])
        quality = int(parts[5])

        # Check the quality
        if quality == 0:
            if rotation:
                self.__rotation = True
            return

        # Check if the distance is within the maximum limit
        if distance < 0 or distance > MAX_DISTANCE_LIMIT:
            if rotation:
                self.__rotation = True
            return

        # Floor the angle to a float with no decimal places
        angle = round(angle, 0)

        # Adjust the angle if the RPLidar is upside down
        if self.__is_upside_down:
            # Subtract the angle from 360
            angle = 360 - angle

        # Check if the angle is already in the distances dictionary
        measure = self.__measures.get(int(angle), None)
        if measure and abs(measure.distance - distance) < DISTANCE_DIFF:
            if rotation:
                self.__rotation = True
            return

        measure = Measure(angle, distance, quality)
        self.__measures[int(angle)] = measure

        # Send the measure to the server
        self.__server_dispatcher.broadcast_rplidar_measure(
            measure
        ) if self.__server_dispatcher else None

        # Check if the rotation is complete
        if rotation or self.__rotation:
            self.__rotation = False

        # Log
        # self.__logger.debug("RPLidar measure: " + str(measure))

        # Increment the messages counter
        self.__messages_counter += 1

    def _update_measures_event_listener(self):
        """
        Listen for the update measures event and process the measures.
        """
        # Start the listener thread
        self.__logger.info("Starting the measures update listener thread...")
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            # Wait for the update measures event to be set
            update = self.__update_measures_event.wait(timeout=self.WAIT_TIMEOUT)
            if not update:
                continue

            # Put the measure in the measures queue
            self.__measures_queue.put(self.__measures)

            # Clear the update measures event
            self.__update_measures_event.clear()

    @final
    def _start(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                raise RuntimeError(
                    "Stop event is set. RPLidar will not run."
                )

            # Check if the RPLidar is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "RPLidar is already running. Cannot start again."
                )

            # Set the started event to signal that the RPLidar has started
            self.__started_event.set()

        # Log
        self.__logger.info("Initialized.")

    def _stop(self) -> None:
        # Ensure the process is cleaned up even if an error occurs
        if self.__process and self.__process.poll() is None:
            # Terminate the process gracefully
            self.__process.terminate()
            self.__process.wait(timeout=self.PROCESS_WAIT_TIMEOUT)

            # If the process is still running, kill it
            if self.__process.poll() is None:
                self.__process.kill()

            # Wait for the process to finish
            self.__process.wait()
            self.__process = None

        # Wait for the listener for measures updates to finish
        if self.__update_measures_listener_thread:
            self.__update_measures_listener_thread.join()
            self.__update_measures_listener_thread = None

        with self.__rlock:
            # Clear the started event
            self.__started_event.clear()

            # Clear the deleted event
            self.__deleted_event.clear()

            # Reset the messages counter
            self.__messages_counter = 0

        # Log the stop message
        self.__logger.info("Stopped.")

    @final
    @ignore_sigint
    @log_on_error()
    def run(self):
        # Start the RPLidar
        self._start()

        # Wait for the start event to be set
        self.__logger.info("Waiting for the start event...")
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            if self.__start_event.wait(timeout=self.START_WAIT_TIMEOUT):
                break
        if self.__stop_event.is_set() or self.__deleted_event.is_set():
            # Stop the RPLidar if the stop or deleted event is set
            self._stop()
            return
        self.__logger.info("Started.")

        command = [
            ULTRA_SIMPLE_PATH,
            "--channel",
            "--serial",
            self.__port,
            str(self.__baudrate)
        ]

        try:
            self.__process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Decode output as text
                bufsize=1,  # Line-buffered output
                universal_newlines=True  # Handles different newline characters
            )

        except FileNotFoundError:
            raise ValueError(
                f"The RPLidar ultra_simple executable was not found at {ULTRA_SIMPLE_PATH}. Please ensure it is installed correctly."
            )

        except Exception as e:
            raise RuntimeError(
                f"An error occurred while starting the RPLidar process: {e}"
            )

        try:
            # Read the output in a loop until the process ends or stop event is set
            while self.__process.poll() is None and not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                self._read_output()

            # Stop the RPLidar process
            self._stop()

        except Exception as e:
            # Stop the RPLidar in case of an exception
            self._stop()
            raise e

    def __del__(self):
        """
        Destructor to clean up resources when the RPLidar is no longer needed.
        """
        self.__deleted_event.set()

        # Log
        self.__logger.info(
            "Instance is being deleted. Resources will be cleaned up."
        )
