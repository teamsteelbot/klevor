import os
from multiprocessing import Event, Queue

from .writer import Writer
from ..utils.decorators import ignore_sigint


@ignore_sigint
def writer_target(
    messages_queue: Queue,
    stop_event: Event
) -> None:
    """
    Target function for a multiprocessing process that handles writing log messages.

    Args:
        messages_queue (Queue): Queue to hold log messages.
        stop_event (Event): Event to signal when the process should stop.
    """
    print(
        "Initializing Writer in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the writer
    writer = Writer(
        messages_queue=messages_queue,
        stop_event=stop_event
    )

    # Run the writer
    writer.run()
