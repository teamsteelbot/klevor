import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls

from . import WebSocketServer
from .constants import HOST, PORT


def websocket_server_target(
    messages_queue: Queue,
    parking_event: EventCls,
    stop_event: EventCls,
    writer_messages_queue: Queue,
    host: str = HOST,
    port: int = PORT
) -> None:
    """
    Target function for a multiprocessing process that handles the WebSocket server.

    Args:
        messages_queue (Queue): Queue to broadcast messages through the websockets server.
        parking_event (EventCls): Event to signal the parking state of the server.
        stop_event (EventCls): Event to signal when the websockets server should stop.
        writer_messages_queue (Queue): Queue to hold log messages.
        host (str): The host address for the WebSocket server.
        port (int): The port number for the WebSocket server.
    """
    print(
        "Initializing WebSocketServer in multiprocessing mode. Process ID: ",
        os.getpid()
    )

    # Initialize the websocket server
    server = WebSocketServer(
        messages_queue=messages_queue,
        parking_event=parking_event,
        stop_event=stop_event,
        writer_messages_queue=writer_messages_queue,
        host=host,
        port=port
    )

    # Run the websocket server
    server.run()
