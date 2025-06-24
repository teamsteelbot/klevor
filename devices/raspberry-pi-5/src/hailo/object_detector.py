from multiprocessing import Event, Queue, RLock
from threading import Thread
from typing import final

from . import Hailo
from .abstracts import ObjectDetectorABC
from ..constants import (MODELS_NAME, MODEL_G, MODEL_M, MODEL_R)
from ..env import Env
from ..files import Files
from ..log import Logger
from ..opencv import OpenCV


class ObjectDetector(ObjectDetectorABC):
    """
    Class to handle object detection using Hailo handlers.
    """

    # Logger configuration
    LOGGER_TAG = 'ObjectDetector'

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        model_g_inferences_queue: Queue,
        model_m_inferences_queue: Queue,
        model_r_inferences_queue: Queue,
        start_event: Event,
        parking_event: Event,
        stop_event: Event,
        photographer_images_queue: Queue,
        writer_messages_queue: Queue,
    ) -> None:
        """
        Initialize the ObjectDetector class.

        Args:
            model_g_inferences_queue (Queue): Queue to hold inferences for model G.
            model_m_inferences_queue (Queue): Queue to hold inferences for model M.
            model_r_inferences_queue (Queue): Queue to hold inferences for model R.
            start_event (Event): Event to signal when the object detector should start.
            parking_event (Event): Event to signal the parking state of the robot.
            stop_event (Event): Event to signal when the object detector should stop.
            photographer_images_queue (Queue): Queue to hold input images for processing.
            writer_messages_queue (Queue): Queue to hold log messages.
        """
        # Initialize the queues and events
        self.__photographer_images_queue = photographer_images_queue
        self.__started_event = Event
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__stop_event = stop_event
        self.__processed_images_queues = {}
        self.__stop_events = {}
        self.__inferences_queues = {
            MODEL_G: model_g_inferences_queue,
            MODEL_M: model_m_inferences_queue,
            MODEL_R: model_r_inferences_queue,
        }
        for model_name in MODELS_NAME:
            self.__processed_images_queues[model_name] = Queue()
            self.__stop_events[model_name] = Event()

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the thread
        self.__thread = None

        # Get the YOLO version from the environment variables
        yolo_version = Env.get_yolo_version()

        # Create the Hailo handlers
        self.__hailo_handlers = {}
        self.__hailo_handler_threads: dict[str, Thread | None] = {}
        for model_name in MODELS_NAME:
            # Get the HEF file paths
            hef_file_path = Files.get_model_hailo_suite_compiled_hef_file_path(
                model_name, yolo_version
            )

            # Get the labels file paths
            labels_file_path = Files.get_hailo_labels_file_path(model_name)

            # Get the model class colors
            model_class_colors = OpenCV.get_model_classes_color_palette(
                model_name
            )

            # Create the Hailo handler
            hailo_handler = Hailo(
                model_name=model_name,
                hef_file_path=hef_file_path,
                labels_path=labels_file_path,
                class_colors=model_class_colors,
                processed_images_queue=self.__processed_images_queues[
                    model_name],
                inferences_queue=self.__inferences_queues[model_name],
                stop_event=self.__stop_events[model_name],
                writer_messages_queue=writer_messages_queue
            )
            self.__hailo_handlers[model_name] = hailo_handler

            # Initialize the thread
            self.__hailo_handler_threads[model_name] = None

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    @final
    def run(self) -> None:
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. ObjectDetector will not run."
                )
                return

            # Check if the object detector is already running
            if self.__started_event.is_set():
                self.__logger.warning(
                    "ObjectDetector is already running. Cannot start again."
                )
                return

            # Set the started event to signal that the object detector has started
            self.__started_event.set()

        # Wait for the start event to be set
        self.__start_event.wait()

        for model_name in MODELS_NAME:
            # Initialize the Hailo handler thread
            hailo_handler = self.__hailo_handlers[model_name]
            hailo_handler_thread = Thread(target=hailo_handler.run())

            # Start only the G and R model handlers
            hailo_handler_thread.start() if model_name in [MODEL_G,
                                                           MODEL_R] else None

            # Store the thread in the dictionary
            self.__hailo_handler_threads[model_name] = hailo_handler_thread

        # Process images for G and R models
        self.__logger.info("Starting Hailo handlers for G and R models...")
        while self.is_running() and not self.__parking_event.is_set():
            # Get the image from the photographer images queue
            image = self.__photographer_images_queue.get(
                timeout=self.WAIT_TIMEOUT
            )
            if image is None:
                continue

            # Put the model G and R images in the Hailo handler processed images queues
            for model_name in [MODEL_G, MODEL_R]:
                self.__processed_images_queues[model_name].put(image)

        # Stop the Hailo handlers for G and R models
        for model_name in [MODEL_G, MODEL_R]:
            # Set the stop event for the model handler
            self.__stop_events[model_name].set()

            # Wait for the Hailo handler thread to finish
            self.__logger.info(
                f"Stopping Hailo handler for {model_name} model..."
            )
            self.__hailo_handler_threads[model_name].join()
            self.__hailo_handler_threads[model_name] = None

        # Start the Hailo handler thread for model M
        self.__hailo_handler_threads[MODEL_M].start()

        # Process images for model M
        self.__logger.info("Starting Hailo handler for M model...")
        while self.is_running():
            # Get the image from the photographer images queue
            image = self.__photographer_images_queue.get(
                timeout=self.WAIT_TIMEOUT
            )
            if image is None:
                continue

            # Put the model M image in the Hailo handler processed images queue
            self.__processed_images_queues[MODEL_M].put(image)

        # Stop the Hailo handler thread for model M
        self.__stop_events[MODEL_M].set()

        # Wait for the Hailo handler thread for model M to finish
        self.__logger.info("Stopping Hailo handler for M model...")
        self.__hailo_handler_threads[MODEL_M].join()
        self.__hailo_handler_threads[MODEL_M] = None

        # Clear the started event to signal that the object detector has stopped
        with self.__rlock:
            self.__started_event.clear()

    def __del__(self):
        """
        Destructor to clean up resources when the ObjectDetector is no longer needed.
        """
        self.__stop_event.set()

        # Log
        self.__logger.debug(
            "ObjectDetector instance is being deleted. Resources will be cleaned up."
            )
