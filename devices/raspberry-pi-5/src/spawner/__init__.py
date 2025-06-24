from multiprocessing import Event, Process, Queue, RLock, Value

from ..camera.multiprocessing import photographer_target
from ..env import Env
from ..env.enums import Challenge
from ..hailo.multiprocessing import object_detector_target
from ..log.multiprocessing import writer_target
from ..opencv import OpenCV
from ..pilot.multiprocessing import pilot_target
from ..rplidar.multiprocessing import rplidar_target
from ..serial_communication.multiprocessing import serial_communication_target


class Spawner:
    """
    Class that spawns processes for the challenge.
    """

    def __init__(self, movement: bool = True):
        """
        Initialize the Spawner class.

        Args:
            movement (bool): Flag to indicate if the pilot should handle movement.
        """
        # Get the debug mode form environment variables
        self.__debug = Env.get_debug_mode()

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the movement flag
        self.__movement = movement

        # Initialize the queues, values and events
        self.__start_event = Event()
        self.__started_event = Event()
        self.__parking_event = Event()
        self.__stop_event = Event()
        self.__writer_messages_queue = Event()
        self.__writer_stop_event = Event()
        self.__serial_incoming_messages_queue = Queue()
        self.__serial_outgoing_messages_queue = Queue()
        self.__bno08x_yaw_deg = Value('d', 0.0)
        self.__bno08x_turns = Value('i', 0)
        self.__rplidar_update_measures_event = Event()
        self.__rplidar_measures_queue = Queue()
        self.__photographer_capture_image_event = None
        self.__photographer_images_queue = None
        self.__photographer_preprocess_fn = OpenCV.preprocess_pil_image
        self.__object_detector_model_g_inferences_queue = None
        self.__object_detector_model_m_inferences_queue = None
        self.__object_detector_model_r_inferences_queue = None

        # Initialize the processes
        self.__writer_process = None
        self.__serial_communication_process = None
        self.__rplidar_process = None
        self.__photographer_process = None
        self.__object_detector_process = None
        self.__pilot_process = None

    def run(self) -> None:
        """
        Run the spawner to initialize and manage the challenge processes.
        """
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                print("Stop event is set. RPLidar will not run.")
                return

            # Check if the RPLidar is already running
            if self.__started_event.is_set():
                print("Spawner is already running. Cannot start again.")
                return

            # Set the started event to signal that the Spawner has started
            self.__started_event.set()

        # Start the writer process
        self.__writer_process = Process(
            target=writer_target,
            args=(self.__writer_messages_queue, self.__writer_stop_event)
        )
        self.__writer_process.start()

        # Start the serial communication process
        self.__serial_communication_process = Process(
            target=serial_communication_target,
            args=(self.__start_event,
                  self.__parking_event,
                  self.__stop_event,
                  self.__serial_incoming_messages_queue,
                  self.__serial_outgoing_messages_queue,
                  self.__writer_messages_queue,
                  self.__bno08x_yaw_deg,
                  self.__bno08x_turns,
                  self.__photographer_capture_image_event)
        )
        self.__serial_communication_process.start()

        # Initialize the RPLidar process
        self.__rplidar_process = Process(
            target=rplidar_target,
            args=(self.__rplidar_update_measures_event,
                  self.__rplidar_measures_queue,
                  self.__start_event,
                  self.__stop_event,
                  self.__writer_messages_queue)
        )
        self.__rplidar_process.start()

        # Wait for the start event to be set
        self.__start_event.wait()

        # Get the challenge from the environment variables
        challenge = Env.get_challenge()

        # Check if the challenge requires the photographer and the object detector
        if challenge == Challenge.WITH_OBSTACLES:
            # Initialize the required queues and events for the photographer and object detector
            self.__photographer_capture_image_event = Event()
            self.__photographer_images_queue = Queue()
            self.__object_detector_model_g_inferences_queue = Queue()
            self.__object_detector_model_m_inferences_queue = Queue()
            self.__object_detector_model_r_inferences_queue = Queue()

            # Initialize the photographer process
            self.__photographer_process = Process(
                target=photographer_target,
                args=(self.__photographer_images_queue,
                      self.__photographer_capture_image_event,
                      self.__stop_event,
                      self.__writer_messages_queue,
                      OpenCV.preprocess_pil_image)
            )
            self.__photographer_process.start()

            # Initialize the object detector process
            self.__object_detector_process = Process(
                target=object_detector_target,
                args=(self.__object_detector_model_g_inferences_queue,
                      self.__object_detector_model_m_inferences_queue,
                      self.__object_detector_model_r_inferences_queue,
                      self.__start_event,
                      self.__parking_event,
                      self.__stop_event,
                      self.__photographer_images_queue,
                      self.__writer_messages_queue)
            )
            self.__object_detector_process.start()

        # Initialize the pilot process
        self.__pilot_process = Process(
            target=pilot_target,
            args=(self.__start_event,
                  self.__parking_event,
                  self.__stop_event,
                  self.__rplidar_update_measures_event,
                  self.__rplidar_measures_queue,
                  self.__serial_incoming_messages_queue,
                  self.__serial_outgoing_messages_queue,
                  self.__writer_messages_queue,
                  self.__bno08x_yaw_deg,
                  self.__bno08x_turns,
                  self.__movement,
                  self.__photographer_capture_image_event,
                  self.__object_detector_model_g_inferences_queue,
                  self.__object_detector_model_m_inferences_queue,
                  self.__object_detector_model_r_inferences_queue)
        )
        self.__pilot_process.start()

        # Wait for all processes to finish
        self.__serial_communication_process.join() if self.__serial_communication_process else None
        self.__rplidar_process.join() if self.__rplidar_process else None
        self.__photographer_process.join() if self.__photographer_process else None
        self.__object_detector_process.join() if self.__object_detector_process else None
        self.__pilot_process.join() if self.__pilot_process else None

        # Set the writer stop event to stop the writer process
        self.__writer_stop_event.set()
        self.__writer_process.join() if self.__writer_process else None

    def __del__(self):
        """
        Destructor to clean up resources when the Spawner is no longer needed.
        """
        self.__stop_event.set()

        print(
            "Spawner instance is being deleted. Resources will be cleaned up."
        )
