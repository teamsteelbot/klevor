import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls

from .writer import Writer


def writer_target(
    debug: bool,
    messages_queue: Queue,
    stop_event: EventCls
) -> None:
    """
    Target function for a multiprocessing process that handles writing log messages.

    Args:
        debug (bool): Flag to indicate if the writer is in debug mode.
        messages_queue (Queue): Queue to hold log messages.
        stop_event (EventCls): Event to signal when the process should stop.
    """
    print(
        "Initializing Writer in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the writer
    writer = Writer(
        debug=debug,
        messages_queue=messages_queue,
        stop_event=stop_event
    )

    # Run the writer
    writer.run()
