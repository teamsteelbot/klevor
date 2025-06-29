import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls
from multiprocessing.sharedctypes import Value as ValueCls
from typing import Optional

from . import Pilot


def pilot_target(
    debug: bool,
    challenge: ValueCls,
    start_event: EventCls,
    parking_event: EventCls,
    stop_event: EventCls,
    completed_event: EventCls,
    rplidar_update_measures_event: EventCls,
    rplidar_measures_queue: Queue,
    serial_sender_messages_queue: Queue,
    writer_messages_queue: Queue,
    bno08x_yaw_deg: ValueCls,
    bno08x_turns: ValueCls,
    movement: bool = True,
    photographer_capture_image_event: Optional[EventCls] = None,
    detector_model_g_inferences_queue: Optional[Queue] = None,
    detector_model_m_inferences_queue: Optional[Queue] = None,
    detector_model_r_inferences_queue: Optional[Queue] = None,
) -> None:
    """
    Target function for a multiprocessing process that handles the Pilot.

    Args:
        debug (bool): Flag to indicate if the pilot is in debug mode.
        challenge (ValueCls): Shared value to hold the current challenge.
        start_event (EventCls): Event to signal when the pilot should start.
        parking_event (EventCls): Event to signal the parking state of the robot.
        stop_event (EventCls): Event to signal when the pilot should stop.
        completed_event (EventCls): Event to signal when the challenge has been completed successfully.
        rplidar_update_measures_event (Event): Event to signal when the RPLidar should update measures.
        rplidar_measures_queue (Queue): Queue to hold RPLidar measures.
        serial_sender_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
        writer_messages_queue (Queue): Queue to hold log messages.
        bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
        bno08x_turns (ValueCls): Shared value for the BNO08X turns.
        movement (bool): Flag to indicate if the pilot should handle movement.
        photographer_capture_image_event (Optional[EventCls]): Event to signal when the photographer should capture an image.
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
        debug=debug,
        challenge=challenge,
        start_event=start_event,
        parking_event=parking_event,
        stop_event=stop_event,
        completed_event=completed_event,
        rplidar_update_measures_event=rplidar_update_measures_event,
        rplidar_measures_queue=rplidar_measures_queue,
        serial_sender_messages_queue=serial_sender_messages_queue,
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
