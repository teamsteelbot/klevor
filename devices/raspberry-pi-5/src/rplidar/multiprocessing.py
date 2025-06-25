import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls
from typing import Optional

from . import RPLidar
from .constants import (
    RPLIDAR_C1_BAUDRATE, RPLIDAR_C1_PORT,
)


def rplidar_target(
    update_measures_event: EventCls,
    measures_queue: Queue,
    start_event: EventCls,
    stop_event: EventCls,
    writer_messages_queue: Queue,
    server_messages_queue: Optional[Queue] = None,
    baudrate: int = RPLIDAR_C1_BAUDRATE,
    port: str = RPLIDAR_C1_PORT,
    is_upside_down: bool = True
) -> None:
    """
    Target function for a multiprocessing process that handles the RPLidar.

    Args:
        update_measures_event (EventCls): Event to signal when the RPLidar should update measures.
        measures_queue (Queue): Queue to hold the measures from the RPLidar.
        start_event (EventCls): Event to signal when the RPLidar should start.
        stop_event (EventCls): Event to signal when the RPLidar should stop.
        writer_messages_queue (Queue): Queue to hold log messages.
        server_messages_queue (Optional[Queue]): Queue to broadcast messages through the websockets server.
        baudrate (int): Baud rate for the serial communication.
        port (str): SerialCommunication port for the RPLidar.
        is_upside_down (bool): If True, the RPLidar is upside down, and angles will be adjusted accordingly.
    """
    print(
        "Initializing RPLidar in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the RPLidar
    rplidar = RPLidar(
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

    # Run the RPLidar
    rplidar.run()
