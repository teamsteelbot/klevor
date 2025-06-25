import os
from multiprocessing import Event, Queue, Value
from multiprocessing.synchronize import Event as EventCls
from multiprocessing.sharedctypes import Value as ValueCls
from typing import Optional

from . import SerialCommunication
from .constants import (
    RASPBERRY_PI_PICO_BAUDRATE,
    RASPBERRY_PI_PICO_CONSOLE_PORT,
    RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
    RASPBERRY_PI_PICO_DATA_PORT,
    RASPBERRY_PI_PICO_DATA_PORT_ALT,
)


def serial_communication_target(
    start_event: EventCls,
    parking_event: EventCls,
    stop_event: EventCls,
    incoming_messages_queue: Queue,
    outgoing_messages_queue: Queue,
    writer_messages_queue: Queue,
    bno08x_yaw_deg: ValueCls,
    bno08x_turns: ValueCls,
    photographer_capture_image_event: EventCls,
    server_messages_queue: Optional[Queue] = None,
    console_port: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT,
    console_port_alt: Optional[str] = RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
    data_port: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT,
    data_port_alt: Optional[str] = RASPBERRY_PI_PICO_DATA_PORT_ALT,
    baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE
) -> None:
    """
    Target function for a multiprocessing process that handles the serial
    communication.

    Args:
        start_event (EventCls): Event to signal when the serial communication has started.
        parking_event (EventCls): Event to signal the parking state of the robot.
        stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
        incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
        outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
        writer_messages_queue (Queue): Queue to hold log messages.
        bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
        bno08x_turns (ValueCls): Shared value for the BNO08X turns.
        photographer_capture_image_event (EventCls): Event to signal when an image should be captured.
        server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
        console_port (Optional[str]): Serial port used for receiving data from Pico.
        console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
        data_port (Optional[str]): Serial port used for sending data to Pico.
        data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
        baudrate (Optional[int]): Baud rate for the serial communication.
    """
    print(
        "Initializing SerialCommunication in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the serial communication
    serial_communication = SerialCommunication(
        start_event=start_event,
        parking_event=parking_event,
        stop_event=stop_event,
        incoming_messages_queue=incoming_messages_queue,
        outgoing_messages_queue=outgoing_messages_queue,
        writer_messages_queue=writer_messages_queue,
        bno08x_yaw_deg=bno08x_yaw_deg,
        bno08x_turns=bno08x_turns,
        photographer_capture_image_event=photographer_capture_image_event,
        server_messages_queue=server_messages_queue,
        console_port=console_port,
        console_port_alt=console_port_alt,
        data_port=data_port,
        data_port_alt=data_port_alt,
        baudrate=baudrate
    )

    # Run the serial communication
    serial_communication.run()
