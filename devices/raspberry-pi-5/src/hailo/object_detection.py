import threading
from multiprocessing import Event, RLock
from typing import Optional, final

from .abstracts import ObjectDetectionABC
from ..camera.image_processing_queue import Photographer
from ..env import Env
from ..log import LoggerABC
from ..log.sub_logger import SubLogger
from ..utils import is_instance
from ..files import Files
from . import Hailo
from ..constants import (
    MODEL_G, MODEL_M, MODEL_R, MODELS_NAME
)
from ..opencv import OpenCV

class ObjectDetection(ObjectDetectionABC):
    """
    Class to handle object detection using Hailo handlers.
    """

    # Logger configuration
    LOG_TAG = 'ObjectDetection'

    def __init__(self, image_processing_queue: Photographer, logger: Optional[LoggerABC] = None):
        """
        Initialize the ObjectDetection class.

        Args:
            image_processing_queue (Photographer): The queue to process images.
            logger (Optional[LoggerABC]): Logger instance to use for logging. Defaults to None.
        """
        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Check the type of image processing queue
        is_instance(image_processing_queue, Photographer)
        self.__image_processing_queue = image_processing_queue

        # Check the type of logger
        is_instance(logger, LoggerABC) if logger else None

        # Create a sub-logger for the Hailo handler
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

        # Create the stop event
        self.__stop_event = Event()
        self.__stop_event.set()  # Initially set to stop

        # Create the parking event
        self.__parking_event = Event()

        # Initialize the thread
        self.__thread = None

        # Get the YOLO version from the environment variables
        yolo_version = Env.get_yolo_version()

        # Create the Hailo handlers
        self.__hailo_handlers = dict()
        for model_name in MODELS_NAME:
            # Get the HEF file paths
            hef_file_path = Files.get_model_hailo_suite_compiled_hef_file_path(model_name, yolo_version)

            # Get the labels file paths
            labels_file_path = Files.get_hailo_labels_file_path(model_name)

            # Get the model class colors
            model_class_colors = OpenCV.get_model_classes_color_palette(model_name)

            # Create the Hailo handler
            hailo_handler = Hailo(model_name, hef_file_path, labels_file_path, model_class_colors,
                                  image_processing_queue=image_processing_queue, logger=logger,
                                  put_output_inference_fn=image_processing_queue.add_inference)
            self.__hailo_handlers[model_name] = hailo_handler
            
    def __start(self) -> None:
        """
        Clear the stop and parking events
        """
        with self.__rlock:
            # Clear the stop event
            self.__stop_event.clear()

            # Clear the parking event
            self.__parking_event.clear()

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self) -> None:
        """
        Set the stop event to stop the object detection.
        """
        with self.__rlock:
            # Set the stop event
            self.__stop_event.set()

            # Clear the parking event
            self.__parking_event.clear()

    @final
    def is_stopped(self) -> bool:
        with self.__rlock:
            return self.__stop_event.is_set()

    @final
    def set_parking_event(self) -> None:
        with self.__rlock:
            self.__parking_event.set()

    @final
    def _loop(self)-> None:
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
                self.__logger.warning('Object detection threads are already running.') if self.__logger else None
                return

            # Start the object detection loop thread
            self.__start()
            self.__thread = threading.Thread(target=self._loop)
            self.__thread.start()

        # Log
        self.__logger.info('Object detection threads started.') if self.__logger else None

    def stop_thread(self) -> None:
        """
        Stop the object detection thread.
        """
        with self.__rlock:
            # Check if the thread is not running
            if self.is_stopped():
                self.__logger.warning('Object detection threads are already stopped.') if self.__logger else None
                return

            # Stop the object detection loop
            self.__stop()

            # Wait for the thread to finish
            self.__thread.join()
            self.__thread = None

        # Log
        self.__logger.info('Object detection threads stopped.') if self.__logger else None

    def __del__(self):
        """
        Destructor to ensure the thread is stopped when the object is deleted.
        """
        self.stop_thread() if self.is_running() else None
        self.__logger.info('ObjectDetection instance deleted.') if self.__logger else None