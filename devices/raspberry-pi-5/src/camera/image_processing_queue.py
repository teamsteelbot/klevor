from multiprocessing import Queue, Event, RLock
from threading import Thread
from typing import Optional, Callable, final

import numpy as np
from PIL.Image import Image

from .abstracts import CameraABC, ImageProcessingQueueABC
from ..model.image_bounding_boxes import ImageBoundingBoxes
from ..server.abstracts import WebsocketsServerABC
from ..utils import check_type
from ..log.abstracts import LoggerABC
from ..log.sub_logger import SubLogger


class ImageProcessingQueue(ImageProcessingQueueABC):
    """
    Class for managing a queue of images for processing in a real-time tracking system.
    """
    # Logger configuration
    LOG_TAG = "ImagesQueue"

    def __init__(self, camera: CameraABC, logger: Optional[LoggerABC] = None, server: Optional[WebsocketsServerABC]=None):
        """
        Initialize the image processing queue.

        Args:
            camera (CameraABC): Camera instance for capturing images.
            logger (Optional[Logger]): Logger instance for logging messages.
            server (Optional[WebsocketsServerABC]): Websockets server instance for real-time tracking updates.
        """
        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the stop event
        self.__stop_event = Event()
        self.__stop_event.set()

        # Check the type of camera
        check_type(camera, CameraABC)
        self.__camera = camera

        # Check the type of server
        check_type(server, WebsocketsServerABC) if server else None
        self.__server = server

        # Check the type of logger
        check_type(logger, LoggerABC) if logger else None

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

    @final
    def add_image(self, image: Image) -> None:
        # Check the type of the image
        check_type(image, Image)

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
        self.__server.send_original_image(image) if self.__server else None

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
    def wait_pending_input_image_event(self) -> None:
        self.__pending_input_image_event.wait()

    @final
    def wait_pending_output_inference_event(self) -> None:
        self.__pending_output_inference_event.wait()

    @final
    def __loop(self):
        """
        Loop to capture images and put them in the input image processing queue.
        """
        while self.is_running():
            # Wait for the capture image event
            self.__capture_image_event.wait()

            # Capture image from camera
            self.capture_image()

            # Clear the capture image event
            self.__capture_image_event.clear()

        # Log
        self.__logger.info("Image processing queue loop stopped.") if self.__logger else None

    @final
    def __start(self) -> None:
        """
        Start the image processing queue.
        """
        with self.__rlock:
            # Check if it has already been started
            if self.is_running():
                self.__logger.warning("Image processing queue already started.") if self.__logger else None
                return

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

    @final
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
            self.__thread = Thread(target=self.__loop)
            self.__thread.start()

            # Log
            self.__logger.info("Image processing queue thread started.") if self.__logger else None

    @final
    def stop_thread(self) -> None:
        with self.__rlock:
            # Stop the image processing queue
            self.__stop()

            # Wait for the thread to finish
            if self.__thread:
                self.__thread.join()
                self.__thread = None

            # Log
            self.__logger.info("Image processing queue thread stopped.") if self.__logger else None

    def __del__(self):
        """
        Destructor for the image processing queue.
        """
        # Stop the image processing queue thread
        self.stop_thread() if self.__thread else None