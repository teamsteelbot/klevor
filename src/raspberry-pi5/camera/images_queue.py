from multiprocessing import Queue, Event, Lock

from PIL.Image import Image

from camera import Camera
from log import Logger
from model.image_bounding_boxes import ImageBoundingBoxes
from server import RealtimeTrackerServer


class ImagesQueue:
    """
    Queue for images to be processed.
    """
    __imager_counter = 0
    __lock = None
    __log_tag = "ImagesQueue"
    __logger = None
    __camera = None
    __server = None
    __capture_image_event = None
    __pending_input_image_event = None
    __pending_output_inference_event = None
    __input_images_queue = None
    __output_inference_queue = None
    __stop_event = None

    def __init__(self, stop_event: Event, logger: Logger, camera: Camera, server=RealtimeTrackerServer):
        """
        Initialize the images queue.

        Args:
            stop_event (Event): Event to signal when to stop processing.
            logger (Logger): Logger instance for logging messages.
            camera (Camera): Camera instance for capturing images.
            server (RealtimeTrackerServer): Server instance for real-time tracking updates.
        """
        # Initialize the lock
        self.__lock = Lock()

        # Check the type of the stop event
        if not isinstance(stop_event, Event):
            raise ValueError("stop_event must be an instance of Event")
        self.__stop_event = stop_event

        # Check the type of the camera
        if not isinstance(camera, Camera):
            raise ValueError("camera must be an instance of Camera")
        self.__camera = camera

        # Check the type of the server
        if not isinstance(server, RealtimeTrackerServer):
            raise ValueError("server must be an instance of RealtimeTrackerServer")
        self.__server = server

        # Check the type of the logger
        if not isinstance(logger, Logger):
            raise ValueError("logger must be an instance of Logger")

        # Get the sub-logger for this class
        self.__logger = logger.get_sub_logger(self.__log_tag)

        # Initialize the events
        self.__capture_image_event = Event()
        self.__pending_input_image_event = Event()
        self.__pending_output_inference_event = Event()
        self.__stop_event = stop_event

    def put_input_image(self, image: Image) -> None:
        """
        Put image in input images queue.

        Args:
            image (Image): Image to put in the input images queue.
        """
        # Check the type of the image
        if not isinstance(image, Image):
            raise ValueError("image must be an instance of PIL.Image.Image")

        with self.__lock:
            # Put image in input images queue
            self.__input_images_queue.put(image)

            # Set the pending input image event
            self.__pending_input_image_event.set()

            # Increment the image counter
            counter = self.__imager_counter
            self.__imager_counter += 1

        # Log
        self.__logger.log(f"Image {counter} added to input images queue.")

    def get_input_image(self) -> Image|None:
        """
        Get image from input images queue.

        Returns:
            Image|None: Image from the input images queue or None if no image is available.
        """
        with self.__lock:
            # Check if the pending input image event is set
            if self.__pending_input_image_event.is_set():
                return None
            
            # Get the image from input images queue
            image = self.__input_images_queue.get()
            
            # Clear the pending input image event
            if self.__input_images_queue.empty():
                self.__pending_input_image_event.clear()

        # Log
        self.__logger.log(f"Image retrieved from input images queue.")

        # Send image to server
        if self.__server:
            self.__server.send_image_original(image)

        return image
        
    def put_output_inference(self, inference:ImageBoundingBoxes) -> None:
        """
        Put inference in output inference queue.

        Args:
            inference (ImageBoundingBoxes): Inference to put in the output inference queue.
        """
        with self.__lock:
            # Put inference in output inference queue
            self.__output_inference_queue.put(inference)

            # Set the pending output inference event
            self.__pending_output_inference_event.set()

        # Log
        self.__logger.log(f"Inference added to output inference queue.")

    def get_output_inference(self) -> ImageBoundingBoxes|None:
        """
        Get inference from output inference queue.

        Returns:
            ImageBoundingBoxes|None: Inference from the output inference queue or None if no inference is available.
        """
        with self.__lock:
            # Check if the pending output inference event is set
            if self.__pending_output_inference_event.is_set():
                return None

            # Get the inference from output inference queue
            inference = self.__output_inference_queue.get()

            # Clear the pending output inference event
            if self.__output_inference_queue.empty():
                self.__pending_output_inference_event.clear()

        # Log
        self.__logger.log(f"Inference retrieved from output inference queue.")

        return inference

    def capture_image(self):
        """
        Capture image from camera.
        """
        # Capture image from camera
        image_pil = self.__camera.capture_image_pil()

        # Put image in input images queue
        self.put_input_image(image_pil)

    def get_capture_image_event(self) -> Event:
        """
        Get capture image event.

        Returns:
            Event: Event to signal when to capture an image.
        """
        return self.__capture_image_event

    def get_pending_image_event(self) -> Event:
        """
        Get pending input image event.

        Returns:
            Event: Event to signal when an image is pending in the input images queue.
        """
        return self.__pending_input_image_event

    def get_pending_inference_event(self) -> Event:
        """
        Get pending output inference event.

        Returns:
            Event: Event to signal when an inference is pending in the output inference queue.
        """
        return self.__pending_output_inference_event

    def get_stop_event(self) -> Event:
        """
        Get stop event.

        Returns:
            Event: Event to signal when to stop processing.
        """
        return self.__stop_event

    def __clear_events(self):
        """
        Clear the events.
        """
        # Clear the events
        self.__capture_image_event.clear()
        self.__pending_input_image_event.clear()
        self.__pending_output_inference_event.clear()
            
    def start(self):
        """
        Start the images queue.
        """
        with self.__lock:
            # Initialize the queues
            self.__input_images_queue = Queue()
            self.__output_inference_queue = Queue()
    
            # Clear the events
            self.__clear_events()

        # Log
        self.__logger.log("Images queue started.")

    def close(self):
        """
        Close the images queue.
        """
        with self.__lock:
            # Close the queues
            self.__input_images_queue.close()
            self.__output_inference_queue.close()
    
            # Clear the events
            self.__clear_events()

            # Reset the image counter
            self.__imager_counter = 0

        # Log
        self.__logger.log("Images queue closed.")

    def __del__(self):
        """
        Destructor for the images queue.
        """
        # Close the images queue
        self.close()

def main(images_queue: ImagesQueue=None):
    """
    Main function to run the script.
    """
    # Check the type of the images queue
    if not isinstance(images_queue, ImagesQueue):
        raise ValueError("images_queue must be an instance of ImagesQueue")

    # Get the stop event
    stop_event = images_queue.get_stop_event()

    # Get the capture image event
    capture_image_event = images_queue.get_capture_image_event()

    # Start the images queue
    images_queue.start()

    while not stop_event.is_set():
        # Wait for capture image event
        capture_image_event.wait()

        # Capture image from camera
        images_queue.capture_image()

        # Clear the capture image event
        capture_image_event.clear()

    # Close the images queue
    images_queue.close()