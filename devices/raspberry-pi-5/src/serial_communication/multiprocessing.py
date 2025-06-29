import os
from multiprocessing import Queue
from multiprocessing.sharedctypes import Value as ValueCls
from multiprocessing.synchronize import Event as EventCls
from typing import Optional

from . import SerialCommunication
from .constants import (
    RASPBERRY_PI_PICO_BAUDRATE,
    RASPBERRY_PI_PICO_CONSOLE_PORTS,
    RASPBERRY_PI_PICO_DATA_PORTS,
)


def serial_communication_target(
    debug: bool,
    challenge: ValueCls,
    start_event: EventCls,
    stop_event: EventCls,
    bno08x_yaw_deg: ValueCls,
    bno08x_turns: ValueCls,
    sender_messages_queue: Queue,
    writer_messages_queue: Queue,
    server_messages_queue: Optional[Queue] = None,
    console_ports: Optional[list[str]] = RASPBERRY_PI_PICO_CONSOLE_PORTS,
    data_ports: Optional[list[str]] = RASPBERRY_PI_PICO_DATA_PORTS,
    baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
) -> None:
    """
    Target function for a multiprocessing process that handles the serial
    communication.

    Args:
        debug (bool): Flag to indicate if the receiver is in debug mode.
        challenge (ValueCls): Shared value to hold the current challenge.
        start_event (EventCls): Event to signal when the serial communication has started.
        stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
        bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
        bno08x_turns (ValueCls): Shared value for the BNO08X turns.
        sender_messages_queue (Queue): Queue to hold outgoing messages of the serial port.
        writer_messages_queue (Queue): Queue to hold log messages.
        server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
        console_ports (Optional[list[str]]): List of serial ports used for receiving data from Pico.
        data_ports (Optional[list[str]]): List of serial ports used for sending data to Pico.
        baudrate (Optional[int]): Baud rate for the serial communication.
    """
    print(
        "Initializing SerialCommunication in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the serial communication
    serial_communication = SerialCommunication(
        debug=debug,
        challenge=challenge,
        start_event=start_event,
        stop_event=stop_event,
        sender_messages_queue=sender_messages_queue,
        writer_messages_queue=writer_messages_queue,
        bno08x_yaw_deg=bno08x_yaw_deg,
        bno08x_turns=bno08x_turns,
        server_messages_queue=server_messages_queue,
        console_ports=console_ports,
        data_ports=data_ports,
        baudrate=baudrate
    )

    # Run the serial communication
    serial_communication.run()
