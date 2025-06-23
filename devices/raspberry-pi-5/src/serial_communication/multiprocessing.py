import os
from multiprocessing import Queue, Event
from typing import Optional

from . import SerialCommunication
from .constants import (
    RASPBERRY_PI_PICO_CONSOLE_PORT,
    RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
    RASPBERRY_PI_PICO_DATA_PORT,
    RASPBERRY_PI_PICO_DATA_PORT_ALT,
    RASPBERRY_PI_PICO_BAUDRATE
)
from ..utils.decorators import ignore_sigint


@ignore_sigint
def serial_communication_target(opened_event: Event, start_event: Event,
                            parking_event: Event, stop_event: Event,
                            incoming_messages_queue: Queue,
                            outgoing_messages_queue: Queue,
                            writer_messages_queue: Queue,
                            photographer_capture_image_event: Event,
                            server_messages_queue: Optional[Queue] = None,
                            console_port: Optional[
                                str] = RASPBERRY_PI_PICO_CONSOLE_PORT,
                            console_port_alt: Optional[
                                str] = RASPBERRY_PI_PICO_CONSOLE_PORT_ALT,
                            data_port: Optional[
                                str] = RASPBERRY_PI_PICO_DATA_PORT,
                            data_port_alt: Optional[
                                str] = RASPBERRY_PI_PICO_DATA_PORT_ALT,
                            baudrate: Optional[
                                int] = RASPBERRY_PI_PICO_BAUDRATE):
    """
    Target function for a multiprocessing process that handles the serial
    communication.

    Args:
        opened_event (Event): Event to signal when the serial communication is ready to send and receive messages.
        start_event (Event): Event to signal when the serial communication has started.
        parking_event (Event): Event to signal the parking state of the robot.
        stop_event (Event): Event to signal when the serial communication should stop sending and receiving messages.
        incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
        outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
        writer_messages_queue (Queue): Queue to hold log messages.
        photographer_capture_image_event (Event): Event to signal when an image should be captured.
        server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
        console_port (Optional[str]): Serial port used for receiving data from Pico.
        console_port_alt (Optional[str]): Alternative serial port used for receiving data from Pico.
        data_port (Optional[str]): Serial port used for sending data to Pico.
        data_port_alt (Optional[str]): Alternative serial port used for sending data to Pico.
        baudrate (Optional[int]): Baud rate for the serial communication.
    """
    print("Initializing SerialCommunication in multiprocessing mode. Process "
          "ID:",
          os.getpid())

    # Initialize the serial communication
    serial_communication = SerialCommunication(
        opened_event, start_event, parking_event, stop_event,
        incoming_messages_queue, outgoing_messages_queue,
        writer_messages_queue, photographer_capture_image_event,
        server_messages_queue, console_port, console_port_alt,
        data_port, data_port_alt, baudrate
    )

    # Run the serial communication
    serial_communication.run()
