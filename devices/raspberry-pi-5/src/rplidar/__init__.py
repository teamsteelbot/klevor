import subprocess
from multiprocessing import Event, Queue, RLock
from typing import Optional, final

from .abstracts import RPLIDARABC
from .constants import (
    DISTANCE_DIFF,
    RPLIDAR_C1_BAUDRATE,
    RPLIDAR_C1_PORT,
    ULTRA_SIMPLE_PATH,
)
from .measure import Measure
from ..env import Env
from ..log import Logger
from ..server.dispatcher import Dispatcher as WebSocketServerDispatcher
from ..utils import is_instance


class RPLIDAR(RPLIDARABC):
    """
    Class to handle RPLIDAR operations.
    """

    # Logger configuration
    LOGGER_TAG = "RPLIDAR"

    # Process wait timeout
    PROCESS_WAIT_TIMEOUT = 5

    def __init__(
        self,
        measures_queue: Queue,
        start_event: Event,
        stop_event: Event,
        writer_messages_queue: Queue,
        server_messages_queue: Optional[Queue] = None,
        baudrate: int = RPLIDAR_C1_BAUDRATE,
        port: str = RPLIDAR_C1_PORT,
        is_upside_down: bool = True
    ):
        """
        Initialize the RPLIDAR.

        Args:
            measures_queue (Queue): Queue to hold the measures from the RPLIDAR.
            start_event (Event): Event to signal when the RPLIDAR should start.
            stop_event (Event): Event to signal when the RPLIDAR should stop.
            writer_messages_queue (Queue): Queue to hold log messages.
            server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server.
            baudrate (int): Baud rate for the serial communication.
            port (str): SerialCommunication port for the RPLIDAR.
            is_upside_down (bool): If True, the RPLIDAR is upside down, and angles will be adjusted accordingly.
        """
        # Initialize the queues and events
        self.__measures_queue = measures_queue
        self.__started_event = Event()
        self.__start_event = start_event
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

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

        # Initialize distances dictionary
        self.__distances_dict = {}

        # Messages counter
        self.__messages_counter = 0

        # Initialize the process
        self.__process = None

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    @final
    def _calculate_average_distance(self, angles: list[int]) -> float:
        total_distance = 0.0
        count = 0
        for angle in angles:
            if angle in self.__distances_dict:
                total_distance += self.__distances_dict[angle].distance
                count += 1
        return total_distance / count if count > 0 else 0.0

    @final
    def _after_rotation(self) -> None:
        # Log the end of the rotation
        self.__logger.info("Full rotation completed.")

        # Add the measures dictionary to the measures queue
        self.__measures_queue.put(self.__distances_dict)

        # Reset the distances dictionary
        self.__distances_dict = {}

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

        # Get the angle, distance and quality
        angle = float(parts[1])
        distance = float(parts[3])
        quality = int(parts[5])

        # Check the quality
        if quality == 0:
            return

        # Check if the distance is within the maximum limit
        # if distance < 0 or distance > self.MAX_DISTANCE_LIMIT:
        #    return

        # Floor the angle to a float with no decimal places
        angle = round(angle, 0)

        # Adjust the angle if the RPLIDAR is upside down
        if self.__is_upside_down:
            # Subtract the angle from 360
            angle = 360 - angle

        # Check if the angle is already in the distances dictionary
        if angle in self.__distances_dict:
            self.__measure = Measure(angle, distance, quality)
            self.__distances_dict[angle] = self.__measure

        elif (abs(self.__distances_dict[angle].distance - distance) >
              DISTANCE_DIFF) and (
                abs(self.__distances_dict[angle].distance - distance) >
                DISTANCE_DIFF):
            return

        else:
            # If it is, update the distance and quality
            self.__measure = self.__distances_dict[angle]
            self.__measure.distance = distance
            self.__measure.quality = quality

        # Call the after rotation method if it's the last measure of a full rotation
        self._after_rotation() if rotation else None

        # Send the measure to the server
        self.__server_dispatcher.broadcast_rplidar_measure(
            self.__measure
        ) if self.__server_dispatcher else None

        # Log
        self.__logger.debug(
            "RPLIDAR measure: " + str(
                self.__distances_dict[
                    angle]
                )
            ) if self.__debug else None

        # Increment the messages counter
        self.__messages_counter += 1

    @final
    def run(self):
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. RPLIDAR will not run."
                )
                return

            # Check if the RPLIDAR is already running
            if self.__started_event.is_set():
                self.__logger.warning(
                    "RPLIDAR is already running. Cannot start again."
                )
                return

        # Wait for the start event to be set
        self.__start_event.wait()

        # Set the started event to signal that the RPLIDAR has started
        with self.__rlock:
            self.__started_event.set()

        # Log
        self.__logger.info("RPLIDAR's starting...")

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
                f"The RPLIDAR ultra_simple executable was not found at {ULTRA_SIMPLE_PATH}. Please ensure it is installed correctly."
            )

        except Exception as e:
            raise RuntimeError(
                f"An error occurred while starting the RPLIDAR process: {e}"
            )

        # Read the output in a loop until the process ends or stop event is set
        while self.__process.poll() is None and self.is_running():
            self._read_output()

        # Ensure the process is cleaned up even if an error occurs
        if self.__process and self.__process.poll() is None:
            self.__logger.info(
                "Ensuring process is terminated in finally block..."
            )
            self.__process.terminate()
            self.__process.wait(timeout=self.PROCESS_WAIT_TIMEOUT)
            if self.__process.poll() is None:
                self.__process.kill()
            self.__process.wait()
            self.__process = None

        # Clear the started event
        with self.__rlock:
            self.__start_event.clear()

        # Log the stop message
        self.__logger.info("RPLIDAR process stopped.")

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set() and (
                    self.__process is not None and self.__process.poll() is None)

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the RPLIDAR is no longer needed.
        """
        self.__stop_event.set()

        # Log
        self.__logger.info(
            "RPLIDAR instance is being deleted. Resources will be cleaned up."
            )
