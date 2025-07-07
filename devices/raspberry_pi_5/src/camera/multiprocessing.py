import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls
from typing import Callable, Optional

import numpy as np
from PIL.Image import Image

from . import Camera
from .photographer import Photographer


def photographer_target(
    debug: bool,
    images_queue: Queue,
    capture_image_event: EventCls,
    start_event: EventCls,
    stop_event: EventCls,
    writer_messages_queue: Queue,
    preprocess_fn: Callable[[Image], np.ndarray],
    server_messages_queue: Optional[Queue] = None
):
    """
    Target function for a multiprocessing process that handles photography tasks.

    Args:
        debug (bool): Flag to indicate if the photographer is in debug mode.
        images_queue (Queue): Queue to hold input images for processing.
        capture_image_event (EventCls): Event to signal when an image should be captured.
        start_event (EventCls): Event to signal when the photographer should start.
        stop_event (EventCls): Event to signal when the logger should stop.
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
        debug=debug,
        camera=camera,
        images_queue=images_queue,
        capture_image_event=capture_image_event,
        start_event=start_event,
        stop_event=stop_event,
        writer_messages_queue=writer_messages_queue,
        preprocess_fn=preprocess_fn,
        server_messages_queue=server_messages_queue
    )

    # Run the photographer
    photographer.run()
