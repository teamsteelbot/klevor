import os
from multiprocessing import Event, Queue

from .object_detector import ObjectDetector
from ..utils.decorators import ignore_sigint


@ignore_sigint
def object_detector_target(
    model_g_inferences_queue: Queue,
    model_m_inferences_queue: Queue,
    model_r_inferences_queue: Queue,
    start_event: Event,
    parking_event: Event,
    stop_event: Event,
    photographer_images_queue: Queue,
    writer_messages_queue: Queue,
):
    """
    Target function for a multiprocessing process that handles the
    ObjectDetector.

    Args:
        model_g_inferences_queue (Queue): Queue to hold inferences for model G.
        model_m_inferences_queue (Queue): Queue to hold inferences for model M.
        model_r_inferences_queue (Queue): Queue to hold inferences for model R.
        start_event (Event): Event to signal when the object detector should start.
        parking_event (Event): Event to signal the parking state of the robot.
        stop_event (Event): Event to signal when the object detector should stop.
        photographer_images_queue (Queue): Queue to hold input images for processing.
        writer_messages_queue (Queue): Queue to hold log messages.
    """
    print(
        "Initializing ObjectDetector in multiprocessing mode. Process ID: ",
        os.getpid()
        )

    # Initialize the object detector
    object_detector = ObjectDetector(
        model_g_inferences_queue=model_g_inferences_queue,
        model_m_inferences_queue=model_m_inferences_queue,
        model_r_inferences_queue=model_r_inferences_queue,
        start_event=start_event,
        parking_event=parking_event,
        stop_event=stop_event,
        photographer_images_queue=photographer_images_queue,
        writer_messages_queue=writer_messages_queue
    )

    # Run the object detector
    object_detector.run()
