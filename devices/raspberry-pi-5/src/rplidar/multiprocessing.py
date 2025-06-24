import os
from multiprocessing import Event, Queue
from typing import Optional

from . import RPLIDAR
from .constants import (
    RPLIDAR_C1_BAUDRATE, RPLIDAR_C1_PORT,
)
from ..utils.decorators import ignore_sigint


@ignore_sigint
def rplidar_target(
    update_measures_event: Event,
    measures_queue: Queue,
    start_event: Event,
    stop_event: Event,
    writer_messages_queue: Queue,
    server_messages_queue: Optional[Queue] = None,
    baudrate: int = RPLIDAR_C1_BAUDRATE,
    port: str = RPLIDAR_C1_PORT,
    is_upside_down: bool = True
) -> None:
    """
    Target function for a multiprocessing process that handles the RPLIDAR.

    Args:
        update_measures_event (Event): Event to signal when the RPLIDAR should update measures.
        measures_queue (Queue): Queue to hold the measures from the RPLIDAR.
        start_event (Event): Event to signal when the RPLIDAR should start.
        stop_event (Event): Event to signal when the RPLIDAR should stop.
        writer_messages_queue (Queue): Queue to hold log messages.
        server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server.
        baudrate (int): Baud rate for the serial communication.
        port (str): SerialCommunication port for the RPLIDAR.
        is_upside_down (bool): If True, the RPLIDAR is upside down, and angles will be adjusted accordingly.
    """
    print(
        "Initializing RPLIDAR in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the RPLIDAR
    rplidar = RPLIDAR(
        update_measures_event=update_measures_event,
        measures_queue=measures_queue,
        start_event=start_event,
        stop_event=stop_event,
        writer_messages_queue=writer_messages_queue,
        server_messages_queue=server_messages_queue,
        baudrate=baudrate,
        port=port,
        is_upside_down=is_upside_down
    )

    # Run the RPLIDAR
    rplidar.run()
