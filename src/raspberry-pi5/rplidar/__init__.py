import subprocess
import os
from multiprocessing import Event, RLock
from threading import Thread
from time import sleep
from typing import Optional
import asyncio

from utils import check_type
from log import Logger
from log.sub_logger import SubLogger
from server import RealtimeTrackerServer 
from serial_communication import SerialCommunication
from rplidar.measure import Measure

class RPLIDAR:
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

    # Reading delay
    READING_DELAY = 0.0001  

    # Get the absolute path of the ultra_simple executable
    ULTRA_SIMPLE_PATH = os.path.join(os.path.dirname(__file__), "ultra_simple")

    # Process wait timeout
    PROCESS_WAIT_TIMEOUT = 5

    def __init__(
            self,
            logger: Optional[Logger] = None,
            server: Optional[RealtimeTrackerServer] = None,
            serial: Optional[SerialCommunication] = None,
            baudrate: int = RPLIDAR_C1_BAUDRATE,
            port: str = RPLIDAR_C1_PORT
        ):
        """
        Initialize the RPLIDAR.

        Args:
            logger (Logger|None): Logger instance for logging messages.
            server (RealtimeTrackerServer|None): Server instance for real-time tracking updates.
            serial (SerialCommunication|None): SerialCommunication instance for RPLIDAR.
            baudrate (int): Baud rate for the serial communication.
            port (str): SerialCommunication port for the RPLIDAR.
        """
        # Create the reentrant lock
        self.__rlock = RLock()

        # Create a stop event
        self.__stop_event = Event()

        # Check the type of logger
        if logger:
            check_type(logger, Logger)

            # Get the sub-logger for this class
            self.__logger = SubLogger(logger, self.LOG_TAG)
        else:
            self.__logger = None

        # Check the type of server
        if server:
            check_type(server, RealtimeTrackerServer)
        self.__server = server

        # Check the type of serial communication
        if serial:
            check_type(serial, SerialCommunication)
        self.__serial_communication = serial

        # Check the type of baudrate
        check_type(baudrate, int)
        self.__baudrate = baudrate

        # Check the type of the port
        check_type(port, str)
        self.__port = port

        # Set the start flag
        self.__started = False

        # Distances dictionary
        self.__distances_dict = dict()

        # Messages counter
        self.__messages_counter = 0

        # Initialize the process
        self.__process = None

    def __log(self, message: str, log_to_file = True, print_to_console = True):
        """
        Log a message using the logger if available.
        
        Args:
            message (str): The message to log.
            log_to_file (bool): Whether to log to file using the logger.
            print_to_console (bool): Whether to print the message to console.
        """
        if self.__logger and log_to_file:
            self.__logger.log(message)

        if print_to_console:
            print(f"{self.LOG_TAG}: {message}")

    def __after_a_full_rotation(self):
        """
        Handle actions after a full rotation.
        This method can be overridden to implement custom behavior.
        """
        # Get the measures from the distances dictionary as a string
        measures = list(self.__distances_dict.values())
        measures_str = Measure.measures_to_string(measures)

        # Put the parsed line in the server
        if self.__server and self.__server.is_running():
            asyncio.run(self.__server.broadcast_rplidar_measures(measures_str))

        if self.__serial_communication and self.__serial_communication.is_open() and self.__serial_communication.has_started():
            self.__serial_communication.send_rplidar_measures(measures_str)

        if not self.__server and not self.__serial_communication:
            # Log the output                
            self.__log(f"Full rotation completed with {len(self.__distances_dict)} measures: {measures_str}.", log_to_file=False)

    def __read_output(self):
        """
        Read the output from the RPLIDAR process.
        """
        if not self.__process:
            return

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
        if angle in self.__distances_dict:
            # If it is, update the distance and quality
            self.__distances_dict[angle].distance = distance
            self.__distances_dict[angle].quality = quality
        else:
            # If it is not, add the measure to the distances dictionary
            self.__distances_dict[angle] = Measure(angle, distance, quality)

        # If it's the last measure of a full rotation, handle the full rotation
        if full_rotation:
            # Call the method to handle actions after a full rotation
            self.__after_a_full_rotation()
        
        # Increment the messages counter
        self.__messages_counter += 1

        # Add a small delay to avoid busy-waiting and yield CPU
        sleep(self.READING_DELAY)

    def __loop(self):
        """
        Loop to read the output from the RPLIDAR process.
        """
        with self.__rlock:
            if self.__started:
                self.__log("RPLIDAR is already started.")
                return

        # Log the start of the RPLIDAR process
        self.__log("Starting RPLIDAR process...")

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
        
        # Set the started flag to True
        self.__started = True

        # Read the output in a loop until the process ends or stop event is set
        if not self.__stop_event:
            try:
                while self.__process.poll() is None:
                    self.__read_output()

            except KeyboardInterrupt:
                self.__stop()
        else:
            # Read the output in a loop until the process ends or stop event is set
            while self.__process.poll() is None and not self.__stop_event.is_set():
                self.__read_output()

        # Set the started flag to False if the process ends
        self.__started = False

    def __stop(self):
        """
        Stop the RPLIDAR process.
        """
        if not self.__started:
            return

        # Set the stop event
        self.__stop_event.set()

        # Ensure the process is cleaned up even if an error occurs
        if self.__process and self.__process.poll() is None:
            self.__log("Ensuring process is terminated in finally block...")
            self.__process.terminate()
            self.__process.wait(timeout=self.PROCESS_WAIT_TIMEOUT)
            if self.__process.poll() is None:
                self.__process.kill()
            self.__process.wait()

        # Log the stop message
        self.__log("RPLIDAR process stopped.")

    def create_thread(self):
        """
        Create a thread for the RPLIDAR.
        """
        with self.__rlock:
            # Start the RPLIDAR in a separate thread
            thread = Thread(target=self.__loop)
            thread.start()

    def stop_thread(self):
        """
        Stop the RPLIDAR thread.
        """
        with self.__rlock:
            # Stop the RPLIDAR process
            self.__stop()

    def __del__(self):
        """
        Destructor to close the thread if it's started.
        """
        self.__stop()