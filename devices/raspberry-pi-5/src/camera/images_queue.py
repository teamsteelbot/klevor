from multiprocessing import Queue, Event, RLock
from multiprocessing.synchronize import Event as EventCls
from typing import Optional, Callable

import numpy as np
from PIL.Image import Image

from . import Camera
from ..model.image_bounding_boxes import ImageBoundingBoxes
from ..server import RealtimeTrackerServer
from ..utils import check_type
from ..log import Logger
from ..log.sub_logger import SubLogger


class ImagesQueue:
    """
    Queue for images to be processed.
    """
    # Logger configuration
    LOG_TAG = "ImagesQueue"

    def __init__(self, camera: Camera, logger: Optional[Logger] = None, server: Optional[RealtimeTrackerServer]=None):
        """
        Initialize the images queue.

        Args:
            camera (Camera): Camera instance for capturing images.
            logger (Optional[Logger]): Logger instance for logging messages.
            server (Optional[RealtimeTrackerServer]): Server instance for real-time tracking updates.
        """
        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Check the type of camera
        check_type(camera, Camera)
        self.__camera = camera

        # Check the type of server
        check_type(server, RealtimeTrackerServer) if server else None
        self.__server = server

        # Check the type of logger
        check_type(logger, Logger) if logger else None

        # Get the sub-logger for this class
        self.__logger = SubLogger(logger, self.LOG_TAG) if logger else None

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

    def put_input_image(self, image: Image) -> None:
        """
        Put image in input images queue.

        Args:
            image (Image): Image to put in the input images queue.
        """
        # Check the type of the image
        check_type(image, Image)

        with self.__rlock:
            if self.is_stopped():
                self.__logger.warning("Images queue has been stopped. Cannot put image in input images queue.") if self.__logger else None
                return
            
            # Put image in input images queue
            self.__input_images_queue.put(image)

            # Set the pending input image event
            self.__pending_input_image_event.set()

            # Increment the image counter
            counter = self.__imager_counter
            self.__imager_counter += 1

        # Log
        self.__logger.info(f"Image {counter} added to input images queue.") if self.__logger else None

    def get_input_image(self, preprocess_fn: Callable[[Image], np.ndarray]) -> np.ndarray | None:
        """
        Get image from input images queue.

        Returns:
            np.ndarray|None: Preprocessed image from the input images queue or None if no image is available.
        """
        with self.__rlock:
            # Check if the pending input image event is set
            if not self.__pending_input_image_event.is_set():
                return None

            # Get the image from input images queue
            image = self.__input_images_queue.get()

            # Preprocess the image
            preprocessed_image = preprocess_fn(image)

            # Clear the pending input image event
            if self.__input_images_queue.empty():
                self.__pending_input_image_event.clear()

        # Log
        self.__logger.debug(f"Image retrieved from input images queue.") if self.__logger else None

        # Send image to server
        self.__server.send_image_original(image) if self.__server else None

        return preprocessed_image

    def put_output_inference(self, model_name: str, inference: ImageBoundingBoxes) -> None:
        """
        Put inference in output inference queue.

        Args:
            model_name (str): Name of the model that produced the inference.
            inference (ImageBoundingBoxes): Inference to put in the output inference queue.
        """
        with self.__rlock:
            if self.is_stopped():
                self.__logger.warning("Images queue has been stopped. Cannot put inference in output inference queue.") if self.__logger else None
                return

            # Put inference in output inference queue
            self.__output_inference_queue.put((model_name, inference))

            # Set the pending output inference event
            self.__pending_output_inference_event.set()

        # Log
        self.__logger.info(f"Inference added to output inference queue for model '{model_name}': {inference}") if self.__logger else None

    def get_output_inference(self) -> tuple[str, ImageBoundingBoxes] | None:
        """
        Get inference from output inference queue.

        Returns:
            tuple[str, ImageBoundingBoxes]|None: Tuple containing model name and inference from the output inference queue or None if no inference is available.
        """
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

    def capture_image(self) -> None:
        """
        Capture image from camera.
        """
        # Capture image from camera
        image_pil = self.__camera.capture_image_pil()

        # Put image in input images queue
        self.put_input_image(image_pil)

    def get_capture_image_event(self) -> EventCls:
        """
        Get capture image event.

        Returns:
            Event: Event to signal when to capture an image.
        """
        return self.__capture_image_event

    def get_pending_image_event(self) -> EventCls:
        """
        Get pending input image event.

        Returns:
            Event: Event to signal when an image is pending in the input images queue.
        """
        return self.__pending_input_image_event

    def __loop(self):
        """
        Loop to capture images and put them in the input images queue.
        """
        while self.is_running():
            # Wait for the capture image event
            self.__capture_image_event.wait()

            # Capture image from camera
            self.capture_image()

            # Clear the capture image event
            self.__capture_image_event.clear()

        # Log
        self.__logger.info("Images queue loop stopped.") if self.__logger else None

    def __start(self) -> None:
        """
        Start the images queue.
        """
        with self.__rlock:
            # Check if it has already been started
            if self.is_running():
                self.__logger.warning("Images queue already started.") if self.__logger else None
                return

            # Initialize the queues
            self.__input_images_queue = Queue()
            self.__output_inference_queue = Queue()

            # Clear the stop event
            self.__stop_event.clear()

        # Log
        self.__logger.info("Images queue started.") if self.__logger else None

    def is_running(self) -> bool:
        """
        Check if the images queue is running.

        Returns:
            bool: True if the images queue is running, False otherwise.
        """
        with self.__rlock:
            return not self.__stop_event.is_set()

    def __stop(self):
        """
        Stop the images queue.
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
        self.__logger.info("Images queue closed.") if self.__logger else None

    def is_stopped(self) -> bool:
        """
        Check if the images queue is stopped.

        Returns:
            bool: True if the images queue is not running, False otherwise.
        """
        with self.__rlock:
            return self.__stop_event.is_set()

    def start_thread(self, thread: Optional[Callable[[], None]] = None) -> None:
        """
        Start the images queue thread.

        Args:
            thread (Optional[Callable[[], None]]): Thread function to run.
        """
        with self.__rlock:
            # Check if the images queue is already running
            if self.is_running():
                self.__logger.warning("Images queue already running.") if self.__logger else None
                return

            # Start the images queue
            self.__start()

            # Start the thread if provided
            if thread:
                self.__thread = thread()
                self.__logger.info("Images queue thread started.") if self.__logger else None

    def __del__(self):
        """
        Destructor for the images queue.
        """
        # Stop the images queue
        self.__stop()