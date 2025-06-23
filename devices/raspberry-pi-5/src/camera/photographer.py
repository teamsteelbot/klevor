from multiprocessing import Queue, Event, RLock
from typing import Optional, Callable, final

import numpy as np
from PIL.Image import Image

from .abstracts import CameraABC, PhotographerABC
from ..log import Logger
from ..server.dispatcher import Dispatcher
from ..utils import is_instance


class Photographer(PhotographerABC):
    """
    Class to handle image processing for the camera.
    """

    # Logger configuration
    LOGGER_TAG = "Photographer"

    # Wait timeout
    WAIT_TIMEOUT = 0.1

    def __init__(self, camera: CameraABC, images_queue: Queue,
                 capture_image_event: Event, stop_event: Event,
                 writer_messages_queue: Queue,
                 preprocess_fn: Callable[[Image], np.ndarray],
                 server_messages_queue: Optional[Queue] = None):
        """
        Initialize the Photographer class.

        Args:
            camera (CameraABC): Camera instance for capturing images.
            images_queue (Queue): Queue to hold input images for processing.
            capture_image_event (Event): Event to signal when an image should be captured.
            stop_event (Event): Event to signal when the photographer should stop processing images.
            writer_messages_queue (Queue): Queue to hold log messages.
            preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
            server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server, if any.
        """
        # Initialize the queues and events
        self.__images_queue = images_queue
        self.__capture_image_event = capture_image_event
        self.__opened_event = Event()
        self.__stop_event = stop_event

        # Check the type of camera
        is_instance(camera, CameraABC)
        self.__camera: CameraABC = camera

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Check the type of preprocess function
        is_instance(preprocess_fn, Callable)
        self.__preprocess_fn = preprocess_fn

        # Initialize the dispatcher for broadcasting messages
        self.__dispatcher = Dispatcher(server_messages_queue,
                                           writer_messages_queue) if server_messages_queue else None

        # Initialize the image counter
        self.__imager_counter = 0

    @final
    def run(self):
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. Photographer will not run.")
                return

            # Check if the photographer is already running
            if self.is_running():
                self.__logger.warning(
                    "Photographer is already running. Cannot start again.")
                return

            # Set the opened event to signal that the photographer is ready
            self.__opened_event.set()

        # Start the photographer
        self.__logger.debug("Photographer's starting...")
        while self.is_running():
            # Wait for the capture image event
            capture_image = self.__capture_image_event.wait(
                timeout=self.WAIT_TIMEOUT)
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
            self.__logger.debug(f"Image {counter} added to images queue.")

            # Clear the capture image event
            self.__capture_image_event.clear()

            # If the dispatcher is available, broadcast the original image
            self.__dispatcher.broadcast_original_image(
                image) if self.__dispatcher else None

        # Clear the events
        self.__capture_image_event.clear()
        with self.__rlock:
            self.__opened_event.clear()

        # Reset the image counter
        self.__imager_counter = 0

        # Log
        self.__logger.debug("Photographer stopped.")

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set() and self.__opened_event.is_set()

    @final
    def is_stopped(self) -> bool:
        return not self.is_running()

    def __del__(self):
        """
        Destructor to clean up resources when the photographer is no longer needed.
        """
        self.__stop_event.set()
