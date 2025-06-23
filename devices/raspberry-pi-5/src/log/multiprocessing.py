from multiprocessing import Queue, Event
from signal import signal, SIGINT, SIG_IGN
import os

from .writer import Writer

def writer_target(messages_queue: Queue, opened_event: Event, stop_event: Event):
    """
    Target function for a multiprocessing process that handles writing log messages.

    Args:
        messages_queue (Queue): Queue to hold log messages.
        opened_event (Event): Event to signal when the logger is ready to write messages.
        stop_event (Event): Event to signal when the process should stop.
    """
    # Ignore the SIGINT signal to prevent the process from being interrupted by Ctrl+C
    signal(SIGINT, SIG_IGN)

    # Initialize the writer
    print("Initializing writer in multiprocessing mode. Process ID:", os.getpid())
    writer = Writer(messages_queue, opened_event, stop_event)

    # Run the writer
    writer.run()