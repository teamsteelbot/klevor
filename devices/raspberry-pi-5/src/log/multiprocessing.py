from multiprocessing import Queue, Event
import os

from .writer import Writer
from ..utils.decorators import ignore_sigint

@ignore_sigint
def writer_target(messages_queue: Queue, opened_event: Event, stop_event: Event):
    """
    Target function for a multiprocessing process that handles writing log messages.

    Args:
        messages_queue (Queue): Queue to hold log messages.
        opened_event (Event): Event to signal when the logger is ready to write messages.
        stop_event (Event): Event to signal when the process should stop.
    """
    print("Initializing Writer in multiprocessing mode. Process ID:", os.getpid())

    # Initialize the writer
    writer = Writer(messages_queue, opened_event, stop_event)

    # Run the writer
    writer.run()