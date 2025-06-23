import subprocess
from multiprocessing import Event, RLock
from threading import Thread
from typing import Optional, final

from .abstracts import RPLIDARABC
from .constants import (
    RPLIDAR_C1_BAUDRATE, RPLIDAR_C1_PORT, ULTRA_SIMPLE_PATH, DISTANCE_DIFF
)
from .measure import Measure
from ..env import Env, Challenge
from ..log.abstracts import LoggerABC
from ..serial_communication import SerialCommunicationABC
from ..serial_communication.enums import RPLIDAR as RPLIDARKey
from ..server import WebSocketServerABC
from ..utils import is_instance


class RPLIDAR(RPLIDARABC):
    """
    Class to handle RPLIDAR operations.
    """

    # Logger configuration
    LOG_TAG = "RPLIDAR"

    # Process wait timeout
    PROCESS_WAIT_TIMEOUT = 5

    def __init__(
            self,
            logger: Optional[LoggerABC] = None,
            server: Optional[WebSocketServerABC] = None,
            serial: Optional[SerialCommunicationABC] = None,
            baudrate: int = RPLIDAR_C1_BAUDRATE,
            port: str = RPLIDAR_C1_PORT,
            is_upside_down: bool = True
    ):
        """
        Initialize the RPLIDAR.

        Args:
            logger (Optional[LoggerABC]): Logger instance for logging messages.
            server (Optional[WebsocketServerABC]): Server instance for real-time tracking updates.
            serial (Optional[SerialCommunicationABC]): SerialCommunication instance for RPLIDAR.
            baudrate (int): Baud rate for the serial communication.
            port (str): SerialCommunication port for the RPLIDAR.
            is_upside_down (bool): If True, the RPLIDAR is upside down, and angles will be adjusted accordingly.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create a stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Create a start event
        self.__start_event = Event()

        # Check the type of logger
        is_instance(logger, LoggerABC) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Check the type of server
        is_instance(server, WebSocketServerABC) if server else None
        self.__server = server

        # Check the type of serial communication
        is_instance(serial, SerialCommunicationABC) if serial else None
        self.__serial_communication = serial

        # Check the type of baudrate
        is_instance(baudrate, int)
        self.__baudrate = baudrate

        # Check the type of the port
        is_instance(port, str)
        self.__port = port

        # Check the type of is_upside_down
        is_instance(is_upside_down, bool)
        self.__is_upside_down = is_upside_down

        # Distances dictionary
        self.__distances_dict = dict()

        # Messages counter
        self.__messages_counter = 0

        # Initialize the process
        self.__process = None

        # Initialize the thread
        self.__thread = None

        # Initialize the challenge
        self.__challenge = None

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

    @final
    @property
    def measures(self) -> dict[float, Measure]:
        """
        Returns the distances dictionary containing the measures.

        Returns:
            dict[float, Measure]: A dictionary with angles as keys and Measure objects as values.
        """
        with self.__rlock:
            return self.__distances_dict

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
        self.__logger.info(
            "Full rotation completed.") if self.__logger else None

        # Put the parsed line in the server
        if self.__server:
            for angle, measure in self.__distances_dict.items():
                measure_str = str(measure)
                self.__server.broadcast_rplidar_measures(str(measure))

        # Send the measure string to the serial communication
        if self.__serial_communication:
            if self.__challenge == Challenge.WITHOUT_OBSTACLES:
                # Calculate the average front, left and right distances by 5 degrees to each side
                avg_front_dist = self._calculate_average_distance(
                    [*range(355, 360), *range(0, 6)])
                avg_left_dist = self._calculate_average_distance(
                    [*range(265, 276)])
                avg_right_dist = self._calculate_average_distance(
                    [*range(85, 96)])

                # Create a dictionary with the average distances
                avg_distances = {
                    RPLIDARKey.FRONT: avg_front_dist,
                    RPLIDARKey.LEFT: avg_left_dist,
                    RPLIDARKey.RIGHT: avg_right_dist
                }

                # Send the average distances to the serial communication
                self.__serial_communication.send_rplidar_measures(avg_distances)

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
        if not angle in self.__distances_dict:
            self.__distances_dict[angle] = Measure(angle, distance, quality)
        else:
            # Check if the distance is negligible
            if self.__distances_dict[
                angle].distance > distance - DISTANCE_DIFF and \
                    self.__distances_dict[
                        angle].distance < distance + DISTANCE_DIFF:
                return

            # If it is, update the distance and quality
            self.__distances_dict[angle].distance = distance
            self.__distances_dict[angle].quality = quality

        # Call the after rotation method if it's the last measure of a full rotation
        if rotation:
            self._after_rotation()

        # Log
        self.__logger.debug("RPLIDAR measure: " + str(self.__distances_dict[
                                                          angle])) if self.__logger and self.__debug else None

        # Increment the messages counter
        self.__messages_counter += 1

    @final
    def _loop(self):
        # Wait for the start event to be set
        self.__start_event.wait()

        # Get the challenge environment variable
        self.__challenge = Env.get_challenge()

        # Log the start of the RPLIDAR process
        self.__logger.info(
            "Starting RPLIDAR process...") if self.__logger else None

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
                f"The RPLIDAR ultra_simple executable was not found at {ULTRA_SIMPLE_PATH}. Please ensure it is installed correctly.")

        except Exception as e:
            raise RuntimeError(
                f"An error occurred while starting the RPLIDAR process: {e}")

        # Read the output in a loop until the process ends or stop event is set
        while self.__process.poll() is None and self.is_running():
            self._read_output()

    @final
    def _start(self):
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

    def start(self):
        with self.__rlock:
            # Set the start event to indicate that the RPLIDAR is starting
            self.__start_event.set()

        # Log
        self.__logger.info("RPLIDAR starting...") if self.__logger else None

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set() and (
                        self.__process is not None and self.__process.poll() is None)

    @final
    def _stop(self):
        with self.__rlock:
            # Set the stop event
            self.__stop_event.set()

            # Clear the start event
            self.__start_event.clear()

            # Ensure the process is cleaned up even if an error occurs
            if self.__process and self.__process.poll() is None:
                self.__logger.info(
                    "Ensuring process is terminated in finally block...") if self.__logger else None
                self.__process.terminate()
                self.__process.wait(timeout=self.PROCESS_WAIT_TIMEOUT)
                if self.__process.poll() is None:
                    self.__process.kill()
                self.__process.wait()
            self.__process = None

        # Log the stop message
        self.__logger.info(
            "RPLIDAR process stopped.") if self.__logger else None

    @final
    def is_stopped(self) -> bool:
        with self.__rlock:
            return not self.is_running()

    def create_thread(self):
        """
        Create a thread for the RPLIDAR.
        """
        with self.__rlock:
            if self.is_running():
                self.__logger.warning(
                    "RPLIDAR thread is already running.") if self.__logger else None
                return

            # Start the RPLIDAR
            self._start()

            # Start the RPLIDAR in a separate thread
            self.__thread = Thread(target=self._loop)
            self.__thread.start()

    def stop_thread(self):
        """
        Stop the RPLIDAR thread.
        """
        with self.__rlock:
            if not self.is_running():
                self.__logger.warning(
                    "RPLIDAR thread is not running.") if self.__logger else None
                return

            # Stop the RPLIDAR
            self._stop()

            # Wait for the thread to finish
            if self.__thread:
                self.__thread.join()
                self.__thread = None

    def __del__(self):
        """
        Destructor to clean up the RPLIDAR object.
        """
        self.stop_thread() if self.__thread else None
        self.__logger.info("RPLIDAR object deleted.") if self.__logger else None
