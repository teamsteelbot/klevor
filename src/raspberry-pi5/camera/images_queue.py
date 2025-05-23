import threading
from multiprocessing import Queue, Event, Lock

from PIL.Image import Image

from camera import Camera

class ImagesQueue:
    """
    Queue for images to be processed.
    """
    __lock = None
    __camera = None
    __capture_image_event = None
    __pending_image_event = None
    __pending_inference_event = None
    __input_images_queue = None
    __output_inference_queue = None
    __stop_event = None

    def __init__(self, camera: Camera=None):
        """
        Initialize the images queue.
        """
        # Initialize the lock
        self.__lock = Lock()

        # Initialize the queues
        self.__input_images_queue = Queue()
        self.__output_inference_queue = Queue()

        # Initialize the camera
        if camera is None:
            raise ValueError("camera cannot be None")
        self.__camera = camera

        # Initialize the events
        self.__capture_image_event = Event()
        self.__pending_image_event = Event()
        self.__pending_inference_event = Event()
        self.__stop_event = Event()

    def put_input_image(self, image: Image) -> None:
        """
        Put image in input images queue.
        """
        with self.__lock:
            # Put image in input images queue
            self.__input_images_queue.put(image)

            # Set the pending image event
            self.__pending_image_event.set()

    def get_input_image(self) -> Image|None:
        """
        Get image from input images queue.
        """
        with self.__lock:
            # Check the input images queue size
            if self.__input_images_queue.qsize() == 0:
                # Clear the pending image event
                self.__pending_image_event.clear()
                return None

            return self.__input_images_queue.get()

    def put_output_inference(self, inference) -> None:
        """
        Put inference in output inference queue.
        """
        with self.__lock:
            # Put inference in output inference queue
            self.__output_inference_queue.put(inference)

            # Set the pending inference event
            self.__pending_inference_event.set()

    def get_output_inference(self):
        """
        Get inference from output inference queue.
        """
        with self.__lock:
            # Check the output inference queue size
            if self.__output_inference_queue.qsize() == 0:
                # Clear the pending inference event
                self.__pending_inference_event.clear()
                return None

            return self.__output_inference_queue.get()

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
        """
        return self.__capture_image_event

    def get_pending_image_event(self) -> Event:
        """
        Get pending image event.
        """
        return self.__pending_image_event

    def get_pending_inference_event(self) -> Event:
        """
        Get pending inference event.
        """
        return self.__pending_inference_event

    def get_stop_event(self) -> Event:
        """
        Get stop event.
        """
        return self.__stop_event
            
    def start(self):
        """
        Start the images queue.
        """
        # Set the stop event
        self.__stop_event.clear()
        
    def stop(self):
        """
        Stop the images queue.
        """
        # Set the stop event
        self.__stop_event.set()

    def __del__(self):
        """
        Destructor for the images queue.
        """
        # Close the queues
        self.__input_images_queue.close()
        self.__output_inference_queue.close()
        
        # Stop the images queue
        self.stop()
        
        # Clear all events
        self.__capture_image_event.clear()
        self.__pending_image_event.clear()
        self.__pending_inference_event.clear()

def main(images_queue: ImagesQueue=None):
    """
    Main function to run the script.
    """
    # Check if the images queue is None
    if images_queue is None:
        raise ValueError("images_queue cannot be None")

    # Get the stop event
    stop_event = images_queue.get_stop_event()

    # Start the images queue
    images_queue.start()

    while stop_event.is_not_set():
        # Wait for capture image event
        self.__capture_image_event.wait()
        self.capture_image()
        self.__capture_image_event.clear()