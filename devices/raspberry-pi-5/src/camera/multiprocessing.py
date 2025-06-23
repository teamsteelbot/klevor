from multiprocessing import Queue, Event
from typing import Optional, Callable
import os

from PIL.Image import Image
import numpy as np

from . import Camera
from .photographer import Photographer
from ..utils.decorators import ignore_sigint

@ignore_sigint
def photographer_target(images_queue: Queue, capture_image_event: Event,
                        opened_event: Event, stop_event: Event, writer_messages_queue: Queue,
                        preprocess_fn: Callable[[Image], np.ndarray],
                        server_messages_queue: Optional[Queue] = None):
    """
    Target function for a multiprocessing process that handles photography tasks.

    Args:
        images_queue (Queue): Queue to hold input images for processing.
        capture_image_event (Event): Event to signal when an image should be captured.
        opened_event (Event): Event to signal when the logger is ready to write messages.
        stop_event (Event): Event to signal when the logger should stop.
        writer_messages_queue (Queue): Queue to hold log messages.
        preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
        server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server, if any.
    """
    print("Initializing Photographer in multiprocessing mode. Process ID:", os.getpid())

    # Initialize the camera
    camera = Camera(writer_messages_queue)

    # Initialize the photographer
    photographer = Photographer(camera, images_queue, capture_image_event,
                                opened_event, stop_event, writer_messages_queue,
                                preprocess_fn, server_messages_queue)

    # Run the photographer
    photographer.run()