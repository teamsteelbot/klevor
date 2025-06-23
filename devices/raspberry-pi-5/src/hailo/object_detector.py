import threading
from multiprocessing import Event, RLock, Queue
from typing import final

from . import Hailo
from .abstracts import ObjectDetectorABC
from ..camera.image_processing_queue import Photographer
from ..constants import (
    MODEL_G, MODEL_M, MODEL_R, MODELS_NAME
)
from ..env import Env
from ..files import Files
from ..log import Logger
from ..opencv import OpenCV
from ..utils import is_instance


class ObjectDetector(ObjectDetectorABC):
    """
    Class to handle object detection using Hailo handlers.
    """

    # Logger configuration
    LOGGER_TAG = 'ObjectDetector'

    def __init__(
            self,
            inferences_queue: Queue,
            started_event: Event,
            start_event: Event,
            parking_event: Event,
            stop_event: Event,
            photographer_images_queue: Queue,
            writer_messages_queue: Queue,
    ) -> None:
        """
        Initialize the ObjectDetection class.

        Args:
            inferences_queue (Queue): Queue to hold the inferences from the Hailo handlers.
            started_event (Event): Event to signal when the object detector has started.
            start_event (Event): Event to signal when the object detector should start.
            parking_event (Event): Event to signal the parking state of the robot.
            stop_event (Event): Event to signal when the object detector should stop.
            photographer_images_queue (Queue): Queue to hold input images for processing.
            writer_messages_queue (Queue): Queue to hold log messages.
        """
        # Initialize the queues and events
        self.__inferences_queue = inferences_queue
        self.__photographer_images_queue = photographer_images_queue
        self.__started_event = started_event
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the thread
        self.__thread = None

        # Get the YOLO version from the environment variables
        yolo_version = Env.get_yolo_version()

        # Create the Hailo handlers
        self.__hailo_handlers = dict()
        for model_name in MODELS_NAME:
            # Get the HEF file paths
            hef_file_path = Files.get_model_hailo_suite_compiled_hef_file_path(
                model_name, yolo_version)

            # Get the labels file paths
            labels_file_path = Files.get_hailo_labels_file_path(model_name)

            # Get the model class colors
            model_class_colors = OpenCV.get_model_classes_color_palette(
                model_name)

            # Create the Hailo handler
            hailo_handler = Hailo(model_name, hef_file_path, labels_file_path,
                                  model_class_colors,
                                  image_processing_queue=image_processing_queue,
                                  logger=logger,
                                  put_output_inference_fn=image_processing_queue.add_inference)
            self.__hailo_handlers[model_name] = hailo_handler

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    @final
    def _loop(self) -> None:
        # Start the Hailo handler for model G and R
        self.__hailo_handlers[MODEL_G].start_thread()
        self.__hailo_handlers[MODEL_R].start_thread()

        # Wait for the stop event
        while self.is_running() and not self.__parking_event.is_set():
            # Wait for the pending image event
            self.__image_processing_queue.wait_pending_input_image_event()

            # Get the image from the image processing queue
            image = self.__image_processing_queue.get_image(Hailo.preprocess)

            # Put the model G and R images in the Hailo handler input queues
            self.__hailo_handlers[MODEL_G].add_image(image)
            self.__hailo_handlers[MODEL_R].add_image(image)

        # Stop the Hailo handlers for G and R models
        self.__hailo_handlers[MODEL_G].stop_thread()
        self.__hailo_handlers[MODEL_R].stop_thread()

        # Start the Hailo handler for model M
        self.__hailo_handlers[MODEL_M].start_thread()

        while self.is_running():
            # Wait for the pending image event
            self.__image_processing_queue.wait_pending_input_image_event()

            # Get the image from the image processing queue
            image = self.__image_processing_queue.get_image(Hailo.preprocess)

            # Put the model M image in the Hailo handler input queue
            self.__hailo_handlers[MODEL_M].add_image(image)

        # Stop the Hailo handler for model M
        self.__hailo_handlers[MODEL_M].stop_thread()

    def start_thread(self) -> None:
        """
        Start the object detection thread.
        """
        with self.__rlock:
            # Check if the threads are already running
            if self.is_running():
                self.__logger.warning(
                    'Object detection threads are already running.') if self.__logger else None
                return

            # Start the object detection loop thread
            self.__start()
            self.__thread = threading.Thread(target=self._loop)
            self.__thread.start()

        # Log
        self.__logger.info(
            'Object detection threads started.') if self.__logger else None

    def stop_thread(self) -> None:
        """
        Stop the object detection thread.
        """
        with self.__rlock:
            # Check if the thread is not running
            if self.is_stopped():
                self.__logger.warning(
                    'Object detection threads are already stopped.') if self.__logger else None
                return

            # Stop the object detection loop
            self.__stop()

            # Wait for the thread to finish
            self.__thread.join()
            self.__thread = None

        # Log
        self.__logger.info(
            'Object detection threads stopped.') if self.__logger else None

    def __del__(self):
        """
        Destructor to ensure the thread is stopped when the object is deleted.
        """
        self.stop_thread() if self.is_running() else None
        self.__logger.info(
            'ObjectDetection instance deleted.') if self.__logger else None
