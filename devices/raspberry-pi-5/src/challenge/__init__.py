from multiprocessing import Process

from ..env.enums import Challenge
from ..env import Env
from ..manager import Manager


class ChallengeHandler:
    """
    Class to handle the challenge logic.
    This class is responsible for managing the challenge state and operations.
    """

    def __init__(self):
        """
        Initialize the ChallengeHandler
        """
        # Initialize the manager
        self.__manager = Manager()

        # Start the manager
        self.__manager.start()

        # Get the debug mode form environment variables
        self.__debug = Env.get_debug_mode()

        # Initialize the logger
        self.__logger = self.__manager.logger()

        # Initialize the server if debug mode is enabled
        self.__server = self.__manager.websockets_server(logger=self.__logger) if self.__debug else None

        # Initialize the serial communication
        self.__serial_communication = self.__manager.serial_communication(logger=self.__logger,
                                                                        server=self.__server)

        # Initialize the RPLIDAR
        self.__rplidar = self.__manager.rplidar(logger=self.__logger,
                                                server=self.__server,
                                                serial=self.__serial_communication)

        # Initialize the camera, image processing queue, and Hailo object detection handler
        self.__camera = None
        self.__image_processing_queue = None
        self.__object_detection = None

    def spawn_processes(self) -> None:
        """
        Spawn the processes for the challenge.
        """
        # Create the logger process
        self.__logger_proc = Process(
            target=self.__logger.create_thread,
        )
        self.__logger_proc.start()

        # Create the server process if debug mode is enabled
        self.__server_proc = Process(
            target=self.__server.create_thread,
        ) if self.__debug else None
        self.__server_proc.start() if self.__server_proc else None

        # Create the serial communication process
        self.__serial_communication_proc = Process(
            target=self.__serial_communication.create_threads,
        )
        self.__serial_communication_proc.start()

        # Create the RPLIDAR process
        self.__rplidar_proc = Process(
            target=self.__rplidar.create_thread,
        )
        self.__rplidar_proc.start()

    def wait_start_event(self) -> None:
        """
        Wait for the start event to be set.
        This method blocks until the start event is set.
        """
        # Wait for the start event from the serial communication
        self.__serial_communication.wait_start_event()

        # Get the challenge from the environment variables
        challenge = Env.get_challenge()

        # Check the type of challenge
        if challenge == Challenge.WITHOUT_OBSTACLES:
            return

        # Initialize the camera
        self.__camera = self.__manager.camera(logger=self.__logger)

        # Initialize the image processing queue
        self.__image_processing_queue = self.__manager.image_processing_queue(logger=self.__logger,
                                                                            camera=self.__camera,
                                                                            server=self.__server)

        # Initialize the Hailo object detection handler
        self.__object_detection = self.__manager.object_detection(logger=self.__logger,
                                                                 image_processing_queue=self.__image_processing_queue,
                                                                 camera=self.__camera,
                                                                 serial_communication=self.__serial_communication)

        # Add the image processing queue to the serial communication
        self.__serial_communication.image_processing_queue = self.__image_processing_queue

        # Create the image processing queue process
        self.__image_processing_queue_proc = Process(
            target=self.__image_processing_queue.create_thread,
        )
        self.__image_processing_queue_proc.start()

        # Create the object detection process
        self.__object_detection_proc = Process(
            target=self.__object_detection.start_thread,
        )
        self.__object_detection_proc.start()

    def wait_stop_event(self) -> None:
        """
        Wait for the stop event to be set.
        This method blocks until the stop event is set.
        """
        # Wait for the stop event from the serial communication
        self.__serial_communication.wait_stop_event()

        # Call the stop method to clean up resources
        self.stop()

    def stop(self):
        """
        Stop the challenge handler and clean up resources.
        """
        # Shutdown the manager
        self.__manager.shutdown() if self.__manager else None

        # Stop the logger thread
        self.__logger.stop_thread() if self.__logger else None

        # Stop the server thread
        self.__server.stop_thread() if self.__server else None

        # Stop the serial communication threads
        self.__serial_communication.stop_threads() if self.__serial_communication else None

        # Stop the RPLIDAR thread
        self.__rplidar.stop_thread() if self.__rplidar else None

        # Stop the image processing queue if it exists
        self.__image_processing_queue.stop_thread() if self.__image_processing_queue else None

        # Stop the Hailo object detection handler if it exists
        self.__object_detection.stop_thread() if self.__object_detection else None

        # Wait for all processes to finish
        self.__logger_proc.join() if self.__logger_proc else None
        self.__server_proc.join() if self.__server_proc else None
        self.__serial_communication_proc.join() if self.__serial_communication_proc else None
        self.__rplidar_proc.join() if self.__rplidar_proc else None
        self.__image_processing_queue_proc.join() if self.__image_processing_queue_proc else None
        self.__object_detection_proc.join() if self.__object_detection_proc else None

    def __del__(self):
        """
        Destructor to clean up resources.
        """
        self.stop()