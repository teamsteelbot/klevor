from multiprocessing import Queue, Event
from typing import Optional, Callable
import os

from PIL.Image import Image
import numpy as np

from . import Camera
from .photographer import Photographer
from ..utils import ignore_sigint

@ignore_sigint
def photographer_target(images_queue: Queue, capture_image_event: Event,
                        opened_event: Event, stop_event: Event, messages_queue: Queue,
                        logger_opened_event: Event, preprocess_fn: Callable[[Image], np.ndarray],
                        original_images_queue: Optional[Queue] = None):
    """
    Target function for a multiprocessing process that handles photography tasks.

    Args:
        images_queue (Queue): Queue to hold input images for processing.
        capture_image_event (Event): Event to signal when an image should be captured.
        opened_event (Event): Event to signal when the logger is ready to write messages.
        stop_event (Event): Event to signal when the logger should stop.
        messages_queue (Queue): Queue to hold log messages.
        logger_opened_event (Event): Event to signal when the logger is ready to write messages.
        preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
        original_images_queue (Optional[Queue]): Queue to hold original images, if any.
    """
    print("Initializing photographer in multiprocessing mode. Process ID:", os.getpid())

    # Initialize the camera
    camera = Camera(messages_queue, logger_opened_event)

    # Initialize the photographer
    photographer = Photographer(camera, images_queue, capture_image_event,
                                opened_event, stop_event, messages_queue,
                                logger_opened_event, preprocess_fn,
                                original_images_queue)

    # Run the photographer
    photographer.run()