import os
from multiprocessing import Event, Queue, Value
from typing import Optional

from . import Pilot
from ..utils.decorators import ignore_sigint


@ignore_sigint
def pilot_target(
    start_event: Event,
    parking_event: Event,
    stop_event: Event,
    rplidar_update_measures_event: Event,
    rplidar_measures_queue: Queue,
    serial_incoming_messages_queue: Queue,
    serial_outgoing_messages_queue: Queue,
    writer_messages_queue: Queue,
    bno08x_yaw_deg: Value,
    bno08x_turns: Value,
    movement: bool = True,
    photographer_capture_image_event: Optional[Event] = None,
    detector_model_g_inferences_queue: Optional[Queue] = None,
    detector_model_m_inferences_queue: Optional[Queue] = None,
    detector_model_r_inferences_queue: Optional[Queue] = None,
) -> None:
    """
    Target function for a multiprocessing process that handles the Pilot.

    Args:
        start_event (Event): Event to signal when the pilot should start.
        parking_event (Event): Event to signal the parking state of the robot.
        stop_event (Event): Event to signal when the pilot should stop.
        rplidar_update_measures_event (Event): Event to signal when the RPLidar should update measures.
        rplidar_measures_queue (Queue): Queue to hold RPLidar measures.
        serial_incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
        serial_outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
        writer_messages_queue (Queue): Queue to hold log messages.
        bno08x_yaw_deg (Value): Shared value for the BNO08X yaw angle in degrees.
        bno08x_turns (Value): Shared value for the BNO08X turns.
        movement (bool): Flag to indicate if the pilot should handle movement.
        photographer_capture_image_event (Optional[Event]): Event to signal when the photographer should capture an image.
        detector_model_g_inferences_queue (Optional[Queue]): Queue for model G inferences.
        detector_model_m_inferences_queue (Optional[Queue]): Queue for model M inferences.
        detector_model_r_inferences_queue (Optional[Queue]): Queue for model R inferences.
    """
    print(
        "Initializing Pilot in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the Pilot
    pilot = Pilot(
        start_event=start_event,
        parking_event=parking_event,
        stop_event=stop_event,
        rplidar_update_measures_event=rplidar_update_measures_event,
        rplidar_measures_queue=rplidar_measures_queue,
        serial_incoming_messages_queue=serial_incoming_messages_queue,
        serial_outgoing_messages_queue=serial_outgoing_messages_queue,
        writer_messages_queue=writer_messages_queue,
        bno08x_yaw_deg=bno08x_yaw_deg,
        bno08x_turns=bno08x_turns,
        movement=movement,
        photographer_capture_image_event=photographer_capture_image_event,
        detector_model_g_inferences_queue=detector_model_g_inferences_queue,
        detector_model_m_inferences_queue=detector_model_m_inferences_queue,
        detector_model_r_inferences_queue=detector_model_r_inferences_queue
    )

    # Run the Pilot
    pilot.run()
