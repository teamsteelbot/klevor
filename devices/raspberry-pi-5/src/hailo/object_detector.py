from queue import Empty
from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from threading import Thread
from typing import final

from . import Hailo
from .abstracts import ObjectDetectorABC
from ..constants import (MODELS_NAME, MODEL_G, MODEL_M, MODEL_R)
from ..files import Files
from ..log import Logger
from ..opencv import OpenCV
from ..utils.decorators import ignore_sigint
from ..log.decorators import log_on_error
from ..log.protocols import LoggerConsumerProtocol


class ObjectDetector(ObjectDetectorABC, LoggerConsumerProtocol):
    """
    Class to handle object detection using Hailo handlers.
    """

    # Logger configuration
    LOGGER_TAG = 'ObjectDetector'

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    # Wait timeout for the start event
    START_WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        debug: bool,
        yolo_version: str,
        model_g_inferences_queue: Queue,
        model_m_inferences_queue: Queue,
        model_r_inferences_queue: Queue,
        start_event: EventCls,
        parking_event: EventCls,
        stop_event: EventCls,
        photographer_images_queue: Queue,
        writer_messages_queue: Queue,
    ) -> None:
        """
        Initialize the ObjectDetector class.

        Args:
            debug (bool): Flag to indicate if the object detector is in debug mode.
            yolo_version (str): The version of YOLO to use for object detection.
            model_g_inferences_queue (Queue): Queue to hold inferences for model G.
            model_m_inferences_queue (Queue): Queue to hold inferences for model M.
            model_r_inferences_queue (Queue): Queue to hold inferences for model R.
            start_event (EventCls): Event to signal when the object detector should start.
            parking_event (EventCls): Event to signal the parking state of the robot.
            stop_event (EventCls): Event to signal when the object detector should stop.
            photographer_images_queue (Queue): Queue to hold input images for processing.
            writer_messages_queue (Queue): Queue to hold log messages.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the queues and events
        self.__photographer_images_queue = photographer_images_queue
        self.__started_event = Event
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__deleted_event = Event()
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
        self.__logger = Logger(writer_messages_queue,
                               tag=self.LOGGER_TAG,
                               debug=self.__debug)

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the thread
        self.__thread = None

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
                debug=debug,
                model_name=model_name,
                hef_file_path=hef_file_path,
                labels_path=labels_file_path,
                class_colors=model_class_colors,
                processed_images_queue=self.__processed_images_queues[
                    model_name],
                inferences_queue=self.__inferences_queues[model_name],
                start_event=self.__start_event,
                stop_event=self.__stop_events[model_name],
                writer_messages_queue=writer_messages_queue
            )
            self.__hailo_handlers[model_name] = hailo_handler

            # Initialize the thread
            self.__hailo_handler_threads[model_name] = None

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _start(self) -> None:
        with (self.__rlock):
            # Check if the stop event is set
            if self.__stop_event.is_set():
                raise RuntimeError(
                    "Stop event is set. ObjectDetector will not run."
                )

            # Check if the object detector is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "ObjectDetector is already running. Cannot start again."
                )

            # Set the started event
            self.__started_event.set()

        # Log
        self.__logger.info("Initialized.")

    @final
    def _stop(self) -> None:
        # Stop the Hailo handler threads
        for model_name in MODELS_NAME:
            # Set the stop event for the model handler
            self.__stop_events[model_name].set()

            # Wait for the Hailo handler thread to finish
            if self.__hailo_handler_threads[model_name] is not None:
                self.__logger.info(
                    f"Stopping Hailo handler for {model_name} model..."
                )
                self.__hailo_handler_threads[model_name].join()
                self.__hailo_handler_threads[model_name] = None

        with self.__rlock:
            # Clear the started event
            self.__started_event.clear()

            # Set the deleted event to signal that the object detector is being deleted
            self.__deleted_event.set()

        # Log
        self.__logger.info("Stopped.")

    @final
    @ignore_sigint
    @log_on_error()
    def run(self) -> None:
        # Start the object detector
        self._start()

        # Wait for the start event to be set
        self.__logger.info("Waiting for the start event...")
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            if self.__start_event.wait(self.START_WAIT_TIMEOUT):
                break
        if self.__stop_event.is_set() or self.__deleted_event.is_set():
            # Stop the object detector if the stop or deleted event is set
            self._stop()
            return
        self.__logger.info("Started.")

        try:
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
            while (not self.__stop_event.is_set() and not
                self.__deleted_event.is_set() and not self.__parking_event.is_set()):
                try:
                    # Get the image from the photographer images queue
                    image = self.__photographer_images_queue.get(
                        timeout=self.WAIT_TIMEOUT
                    )

                except Empty:
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
            while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
                try:
                    # Get the image from the photographer images queue
                    image = self.__photographer_images_queue.get(
                        timeout=self.WAIT_TIMEOUT
                    )

                except Empty:
                    continue

                # Put the model M image in the Hailo handler processed images queue
                self.__processed_images_queues[MODEL_M].put(image)

            # Stop the object detector
            self._stop()

        except Exception as e:
            # Stop the object detector in case of an exception
            self._stop()
            raise e

    def __del__(self):
        """
        Destructor to clean up resources when the ObjectDetector is no longer needed.
        """
        self.__deleted_event.set()

        # Log
        self.__logger.info(
            "Instance is being deleted. Resources will be cleaned up."
        )
