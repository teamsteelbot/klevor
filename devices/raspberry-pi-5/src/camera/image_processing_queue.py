from multiprocessing import Queue, Event, RLock
from threading import Thread
from typing import Optional, Callable, final

import numpy as np
from PIL.Image import Image

from .abstracts import CameraABC, ImageProcessingQueueABC
from ..model import ImageBoundingBoxes
from ..server.abstracts import WebsocketsServerABC
from ..utils import is_instance
from ..log import Logger


class ImageProcessingQueue(ImageProcessingQueueABC):
    """
    Class for managing a queue of images for processing in a real-time tracking system.
    """

    # Logger configuration
    LOG_TAG = "ImagesQueue"

    def __init__(self, camera: CameraABC, messages_queue: Queue, opened_event: Event, server: Optional[WebsocketsServerABC]=None):
        """
        Initialize the image processing queue.

        Args:
            camera (CameraABC): Camera instance for capturing images.
            messages_queue (Queue): Queue to hold log messages.
            opened_event (Event): Event to signal when the logger is ready to write messages.
            server (Optional[WebsocketsServerABC]): Websockets server instance for real-time tracking updates.
        """
        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Check the type of camera
        is_instance(camera, CameraABC)
        self.__camera = camera

        # Initialize the logger
        self.__logger = Logger(messages_queue, opened_event, self.LOG_TAG)
        self.__logger.debug("Initializing image processing queue...")

        # Check the type of server
        is_instance(server, WebsocketsServerABC) if server else None
        self.__server = server

        # Initialize the events
        self.__capture_image_event = Event()
        self.__pending_input_image_event = Event()
        self.__pending_output_inference_event = Event()

        # Set the queues to None
        self.__input_images_queue: Queue[Image] | None = None
        self.__output_inference_queue: Queue[tuple[str, ImageBoundingBoxes]] | None = None

        # Initialize the image counter
        self.__imager_counter = 0

        # Initialize the thread
        self.__thread = None

    @final
    def add_image(self, image: Image) -> None:
        # Check the type of the image
        is_instance(image, Image)

        with self.__rlock:
            if self.is_stopped():
                self.__logger.warning("Image processing queue has been stopped. Cannot put image in input image processing queue.") if self.__logger else None
                return
            
            # Put image in input image processing queue
            self.__input_images_queue.put(image)

            # Set the pending input image event
            self.__pending_input_image_event.set()

            # Increment the image counter
            counter = self.__imager_counter
            self.__imager_counter += 1

        # Log
        self.__logger.info(f"Image {counter} added to input image processing queue.") if self.__logger else None

    @final
    def get_image(self, preprocess_fn: Callable[[Image], np.ndarray]) -> np.ndarray | None:
        with self.__rlock:
            # Check if the pending input image event is set
            if not self.__pending_input_image_event.is_set():
                return None

            # Get the image from input image processing queue
            image = self.__input_images_queue.get()

            # Preprocess the image
            preprocessed_image = preprocess_fn(image)

            # Clear the pending input image event
            if self.__input_images_queue.empty():
                self.__pending_input_image_event.clear()

        # Log
        self.__logger.debug(f"Image retrieved from input image processing queue.") if self.__logger else None

        # Send image to server
        self.__server.broadcast_original_image(image) if self.__server else None

        return preprocessed_image

    @final
    def add_inference(self, model_name: str, inference: ImageBoundingBoxes) -> None:
        with self.__rlock:
            if self.is_stopped():
                self.__logger.warning("Image processing queue has been stopped. Cannot put inference in output inference queue.") if self.__logger else None
                return

            # Put inference in output inference queue
            self.__output_inference_queue.put((model_name, inference))

            # Set the pending output inference event
            self.__pending_output_inference_event.set()

        # Log
        self.__logger.info(f"Inference added to output inference queue for model '{model_name}': {inference}") if self.__logger else None

    @final
    def get_inference(self) -> tuple[str, ImageBoundingBoxes] | None:
        with self.__rlock:
            # Check if the pending output inference event is set
            if not self.__pending_output_inference_event.is_set():
                return None

            # Get the inference from output inference queue
            model_name, inference = self.__output_inference_queue.get()

            # Clear the pending output inference event
            if self.__output_inference_queue.empty():
                self.__pending_output_inference_event.clear()

        # Log
        self.__logger.debug(f"Inference retrieved from output inference queue.") if self.__logger else None

        return model_name, inference

    @final
    def capture_image(self) -> None:
        # Capture image from camera
        image_pil = self.__camera.capture_image_pil()

        # Put image in input image processing queue
        self.add_image(image_pil)

    @final
    def wait_capture_image_event(self) -> None:
        self.__capture_image_event.wait()

    @final
    def set_capture_image_event(self) -> None:
        self.__capture_image_event.set()

    @final
    def wait_pending_input_image_event(self) -> None:
        self.__pending_input_image_event.wait()

    @final
    def wait_pending_output_inference_event(self) -> None:
        self.__pending_output_inference_event.wait()

    @final
    def _loop(self):
        while self.is_running():
            # Wait for the capture image event
            self.__capture_image_event.wait()

            # Capture image from camera
            self.capture_image()

            # Clear the capture image event
            self.__capture_image_event.clear()

        # Log
        self.__logger.info("Image processing queue loop stopped.") if self.__logger else None

    def __start(self) -> None:
        """
        Start the image processing queue.
        """
        with self.__rlock:
            # Initialize the queues
            self.__input_images_queue = Queue()
            self.__output_inference_queue = Queue()

            # Clear the stop event
            self.__stop_event.clear()

        # Log
        self.__logger.info("Image processing queue started.") if self.__logger else None

    @final
    def is_running(self) -> bool:
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self):
        """
        Stop the image processing queue.
        """
        with self.__rlock:
            # Set the stop event
            self.__stop_event.set()

            # Close the queues
            self.__input_images_queue.close()
            self.__output_inference_queue.close()

            # Clear the events
            self.__capture_image_event.clear()
            self.__pending_input_image_event.clear()
            self.__pending_output_inference_event.clear()

            # Reset the image counter
            self.__imager_counter = 0

        # Log
        self.__logger.info("Image processing queue closed.") if self.__logger else None

    @final
    def is_stopped(self) -> bool:
        with self.__rlock:
            return self.__stop_event.is_set()

    @final
    def start_thread(self) -> None:
        with self.__rlock:
            # Check if the image processing queue is already running
            if self.is_running():
                self.__logger.warning("Image processing queue already running.") if self.__logger else None
                return

            # Start the image processing queue
            self.__start()

            # Create a thread for the image processing queue loop
            self.__thread = Thread(target=self._loop)
            self.__thread.start()

        # Log
        self.__logger.info("Image processing queue thread started.") if self.__logger else None

    @final
    def stop_thread(self) -> None:
        with self.__rlock:
            # Check if the image processing queue is already stopped
            if self.is_stopped():
                self.__logger.warning("Image processing queue already stopped.") if self.__logger else None
                return

            # Stop the image processing queue
            self.__stop()

            # Wait for the thread to finish
            self.__thread.join()
            self.__thread = None

        # Log
        self.__logger.info("Image processing queue thread stopped.") if self.__logger else None

    def __del__(self):
        """
        Destructor for the image processing queue.
        """
        self.stop_thread() if self.__thread else None
        self.__logger.info("Image processing queue destroyed.") if self.__logger else None