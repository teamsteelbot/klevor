from multiprocessing import Queue, Event, RLock
from typing import Optional, Callable, final

import numpy as np
from PIL.Image import Image

from .abstracts import CameraABC, PhotographerABC
from ..utils import is_instance
from ..log import Logger
from ..server.enums import Tag
from ..server.message import Message


class Photographer(PhotographerABC):
    """
    Class to handle image processing for the camera.
    """

    # Logger configuration
    LOGGER_TAG = "ImagesQueue"
    
    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(self, camera: CameraABC, images_queue: Queue, capture_image_event: Event, opened_event: Event,
                 stop_event: Event, writer_messages_queue: Queue, preprocess_fn: Callable[[Image], np.ndarray],
                 server_messages_queue: Optional[Queue]=None):
        """
        Initialize the Photographer class.

        Args:
            camera (CameraABC): Camera instance for capturing images.
            images_queue (Queue): Queue to hold input images for processing.
            capture_image_event (Event): Event to signal when an image should be captured.
            opened_event (Event): Event to signal when the logger is ready to write messages.
            stop_event (Event): Event to signal when the logger should stop.
            writer_messages_queue (Queue): Queue to hold log messages.
            preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
            server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server, if any.
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
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)
        self.__logger.debug("Initializing image processing queue...")
        
        # Check the type of preprocess function
        is_instance(preprocess_fn, Callable)
        self.__preprocess_fn = preprocess_fn

        # Initialize the broadcast messages queue if provided
        self.__broadcast_messages_queue = server_messages_queue

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
            capture_image = self.__capture_image_event.wait(timeout=self.WAIT_TIMEOUT)
            if not capture_image:
                continue

            # Capture image stream from camera
            image_stream = self.__camera.capture_image_stream()

            # Convert the image stream to a PIL Image
            image = self.__camera.convert_image_stream_to_pil(image_stream)

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

            # If a broadcast messages queue is provided, send a message
            if self.__broadcast_messages_queue:
                # Send the bytes of the preprocessed image to the broadcast messages queue
                image_stream.seek(0)
                binary_data = image.read()
                self.__broadcast_messages_queue.put(Message(Tag.IMAGE_ORIGINAL, binary_data))

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