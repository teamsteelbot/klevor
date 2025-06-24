import os
from multiprocessing import Event, Queue
from typing import Callable, Optional

import numpy as np
from PIL.Image import Image

from . import Camera
from .photographer import Photographer
from ..utils.decorators import ignore_sigint


@ignore_sigint
def photographer_target(
    images_queue: Queue,
    capture_image_event: Event,
    stop_event: Event,
    writer_messages_queue: Queue,
    preprocess_fn: Callable[[Image], np.ndarray],
    server_messages_queue: Optional[Queue] = None
):
    """
    Target function for a multiprocessing process that handles photography tasks.

    Args:
        images_queue (Queue): Queue to hold input images for processing.
        capture_image_event (Event): Event to signal when an image should be captured.
        stop_event (Event): Event to signal when the logger should stop.
        writer_messages_queue (Queue): Queue to hold log messages.
        preprocess_fn: Callable[[Image], np.ndarray]: Function to preprocess images before inference.
        server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server, if any.
    """
    print(
        "Initializing Photographer in multiprocessing mode. Process ID: ",
        os.getpid()
        )

    # Initialize the camera
    camera = Camera(writer_messages_queue=writer_messages_queue)

    # Initialize the photographer
    photographer = Photographer(
        camera=camera,
        images_queue=images_queue,
        capture_image_event=capture_image_event,
        stop_event=stop_event,
        writer_messages_queue=writer_messages_queue,
        preprocess_fn=preprocess_fn,
        server_messages_queue=server_messages_queue
    )

    # Run the photographer
    photographer.run()
