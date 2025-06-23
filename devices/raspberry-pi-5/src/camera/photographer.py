from multiprocessing import Queue, Event, RLock
from typing import Optional, Callable, final

import numpy as np
from PIL.Image import Image

from .abstracts import CameraABC, ImageProcessingQueueABC
from ..utils import is_instance
from ..log import Logger


class Photographer(ImageProcessingQueueABC):
    """
    Class to handle image processing for the camera.
    """

    # Logger configuration
    LOG_TAG = "ImagesQueue"

    def __init__(self, camera: CameraABC, images_queue: Queue, capture_image_event: Event, opened_event: Event,
                 stop_event: Event, messages_queue: Queue, logger_opened_event: Event,
                 preprocess_fn: Callable[[Image], np.ndarray], original_images_queue: Optional[Queue]=None):
        """
        Initialize the Photographer class.

        Args:
            camera (CameraABC): Camera instance for capturing images.
            images_queue (Queue): Queue to hold input images for processing.
            capture_image_event (Event): Event to signal when an image should be captured.
            opened_event (Event): Event to signal when the logger is ready to write messages.
            stop_event (Event): Event to signal when the logger should stop.
            messages_queue (Queue): Queue to hold log messages.
            logger_opened_event (Event): Event to signal when the logger is ready to write messages.
            preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
            original_images_queue (Optional[Queue]): Queue to hold original images, if any.
        """
        # Check the type of camera
        is_instance(camera, CameraABC)
        self.__camera: CameraABC = camera
        
        # Initialize the queues and events
        self.__images_queue = images_queue
        self.__capture_image_event = capture_image_event
        self.__opened_event = opened_event
        self.__stop_event = stop_event

        # Initialize the logger
        self.__logger = Logger(messages_queue, logger_opened_event, self.LOG_TAG)
        self.__logger.debug("Initializing image processing queue...")
        
        # Check the type of preprocess function
        is_instance(preprocess_fn, Callable)
        self.__preprocess_fn = preprocess_fn

        # Initialize the original images queue if provided
        self.__original_images_queue = original_images_queue

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the image counter
        self.__imager_counter = 0

    @final
    def run(self):
        # Check if the stop event is set
        if self.__stop_event.is_set():
            print("Stop event is set. Image processing queue will not run.")
            return

        # Check if the photographer is already running
        if self.is_running():
            print("Image processing queue is already running. Cannot start again.")
            return

        # Start the photographer
        self.__logger.debug("Starting image processing queue...")
        while self.is_running():
            # Wait for the capture image event
            self.__capture_image_event.wait()

            # Capture image from camera
            image = self.__camera.capture_image_pil()
            
            # Preprocess the image
            preprocessed_image = self.__preprocess_fn(image)

            # Put image in input image processing queue
            self.__images_queue.put(preprocessed_image)

            # Increment the image counter
            counter = self.__imager_counter
            self.__imager_counter += 1

            # Log
            self.__logger.debug(f"Image {counter} added to input image processing queue.")

            # Clear the capture image event
            self.__capture_image_event.clear()

        # Clear the events
        self.__capture_image_event.clear()

        # Reset the image counter
        self.__imager_counter = 0

        # Log
        self.__logger.debug("Image processing queue loop stopped.")

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    @final
    def is_stopped(self) -> bool:
        with self.__rlock:
            return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the photographer is no longer needed.
        """
        self.__stop_event.set()