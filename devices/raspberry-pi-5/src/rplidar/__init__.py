import subprocess
import os
from multiprocessing import Event, RLock
from threading import Thread
from typing import Optional, final
import asyncio

from ..env import Env
from ..utils import check_type
from ..log.abstracts import LoggerABC
from ..log.sub_logger import SubLogger
from ..server import WebsocketsServerABC
from ..serial_communication import SerialCommunicationABC
from .abstracts import RPLIDARABC
from .measure import Measure

class RPLIDAR(RPLIDARABC):
    """
    Class to handle RPLIDAR operations.
    """

    # Logger configuration
    LOG_TAG = "RPLIDAR"

    # RPLIDAR C1 baud rate
    RPLIDAR_C1_BAUDRATE = 460800

    # Default port
    RPLIDAR_C1_PORT = "/dev/ttyUSB0"

    # Max distance limit
    MAX_DISTANCE_LIMIT = 3000

    # Distance difference 
    DISTANCE_DIFF = 25

    # Get the absolute path of the ultra_simple executable
    ULTRA_SIMPLE_PATH = os.path.join(os.path.dirname(__file__), "ultra_simple")

    # Process wait timeout
    PROCESS_WAIT_TIMEOUT = 5

    def __init__(
            self,
            logger: Optional[LoggerABC] = None,
            server: Optional[WebsocketsServerABC] = None,
            serial: Optional[SerialCommunicationABC] = None,
            baudrate: int = RPLIDAR_C1_BAUDRATE,
            port: str = RPLIDAR_C1_PORT
        ):
        """
        Initialize the RPLIDAR.

        Args:
            logger (Optional[LoggerABC]): Logger instance for logging messages.
            server (Optional[WebsocketServerABC]): Server instance for real-time tracking updates.
            serial (Optional[SerialCommunicationABC]): SerialCommunication instance for RPLIDAR.
            baudrate (int): Baud rate for the serial communication.
            port (str): SerialCommunication port for the RPLIDAR.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create a stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Create a start event
        self.__start_event = Event()

        # Check the type of logger
        check_type(logger, LoggerABC) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Check the type of server
        check_type(server, WebsocketsServerABC) if server else None
        self.__server = server

        # Check the type of serial communication
        check_type(serial, SerialCommunicationABC) if serial else None
        self.__serial_communication = serial

        # Check the type of baudrate
        check_type(baudrate, int)
        self.__baudrate = baudrate

        # Check the type of the port
        check_type(port, str)
        self.__port = port

        # Distances dictionary
        self.__distances_dict = dict()

        # Messages counter
        self.__messages_counter = 0

        # Initialize the process
        self.__process = None

        # Initialize the thread
        self.__thread = None

        # Get the debug environment variable
        self.__debug = Env.get_debug_mode()

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
        full_rotation = len(parts) == 7
        if full_rotation:
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

        # Check if the angle is already in the distances dictionary
        if not angle in self.__distances_dict:
            self.__distances_dict[angle] = Measure(angle, distance, quality)
        else:
            # Check if the distance is negligible
            if self.__distances_dict[angle].distance > distance - self.DISTANCE_DIFF and self.__distances_dict[angle].distance < distance + self.DISTANCE_DIFF:
                return

            # If it is, update the distance and quality
            self.__distances_dict[angle].distance = distance
            self.__distances_dict[angle].quality = quality

        # Get the measure string representation
        measure_str = str(self.__distances_dict[angle])

        # Log
        self.__logger.debug("RPLIDAR measure: " + measure_str) if self.__logger and self.__debug else None

        # Put the parsed line in the server
        asyncio.run(self.__server.broadcast_rplidar_measures(measure_str)) if self.__server else None

        # Send the measure string to the serial communication
        self.__serial_communication.send_rplidar_measures(measure_str) if self.__serial_communication else None
        
        # Increment the messages counter
        self.__messages_counter += 1

    @final
    def _loop(self):
        # Wait for the start event to be set
        self.__start_event.wait()

        # Log the start of the RPLIDAR process
        self.__logger.info("Starting RPLIDAR process...") if self.__logger else None

        command = [
            self.ULTRA_SIMPLE_PATH,
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
                text=True, # Decode output as text
                bufsize=1, # Line-buffered output
                universal_newlines=True # Handles different newline characters
            )

        except FileNotFoundError:
            raise ValueError(f"The RPLIDAR ultra_simple executable was not found at {self.ULTRA_SIMPLE_PATH}. Please ensure it is installed correctly.")
        
        except Exception as e:
            raise RuntimeError(f"An error occurred while starting the RPLIDAR process: {e}")

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
            return not self.__stop_event.is_set() and (self.__process is not None and self.__process.poll() is None)

    @final
    def _stop(self):
        with self.__rlock:
            # Set the stop event
            self.__stop_event.set()

            # Clear the start event
            self.__start_event.clear()

            # Ensure the process is cleaned up even if an error occurs
            if self.__process and self.__process.poll() is None:
                self.__logger.info("Ensuring process is terminated in finally block...") if self.__logger else None
                self.__process.terminate()
                self.__process.wait(timeout=self.PROCESS_WAIT_TIMEOUT)
                if self.__process.poll() is None:
                    self.__process.kill()
                self.__process.wait()
            self.__process = None

        # Log the stop message
        self.__logger.info("RPLIDAR process stopped.") if self.__logger else None

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
                self.__logger.warning("RPLIDAR thread is already running.") if self.__logger else None
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
                self.__logger.warning("RPLIDAR thread is not running.") if self.__logger else None
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