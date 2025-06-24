from multiprocessing import Event, Process, Queue, Value
from time import sleep

from .multiprocessing import serial_communication_target
from ..log import Logger
from ..log.multiprocessing import writer_target

if __name__ == "__main__":
    # Create the required queues and events
    writer_messages_queue = Queue()
    writer_stop_event = Event()
    serial_incoming_messages_queue = Queue()
    serial_outgoing_messages_queue = Queue()
    bno08x_turns = Value("i", 0)  # Shared value for BNO08x turns
    photographer_capture_image_event = Event()
    start_event = Event()
    parking_event = Event()
    stop_event = Event()

    # Create a process for the writer
    writer_process = Process(
        target=writer_target, args=(
            writer_messages_queue, writer_stop_event)
        )
    writer_process.start()

    # Create an instance of Logger
    logger = Logger(writer_messages_queue)

    # Create a process for the serial communication
    serial_communication_process = Process(
        target=serial_communication_target,
        args=(serial_incoming_messages_queue, serial_outgoing_messages_queue,
              photographer_capture_image_event, start_event, parking_event,
              stop_event, writer_messages_queue)
    )
    serial_communication_process.start()

    try:
        # Wait indefinitely to keep the serial communication running
        print("SerialCommunication is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)  # Sleep to prevent busy-waiting

    except KeyboardInterrupt:
        # Handle keyboard interrupt to stop the processes gracefully
        print(
            "KeyboardInterrupt received. Stopping serial communication and writer process..."
        )
        logger.warning(
            "KeyboardInterrupt received. Stopping serial communication and writer process..."
        )

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {e}")

    finally:
        # Stop the serial communication and writer process and clean up
        stop_event.set()
        serial_communication_process.join()
        writer_stop_event.set()
        writer_process.join()
