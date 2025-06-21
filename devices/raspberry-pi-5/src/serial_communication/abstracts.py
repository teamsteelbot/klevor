from abc import ABC, abstractmethod

from .message import IncomingMessage, OutgoingMessage, RPLIDAR

class SerialCommunicationABC(ABC):
    """
    Abstract class to handle the serial communication through USB.
    """

    @abstractmethod
    def is_open(self) -> bool:
        """
        Check if the serial port is open, and it's processing outgoing and incoming messages.

        Returns:
            bool: True if the serial port is open and processing messages, False otherwise.
        """
        pass

    @abstractmethod
    def is_closed(self) -> bool:
        """
        Check if the serial port is closed and communication is stopped.

        Returns:
            bool: True if the serial port is closed and communication is stopped, False otherwise.
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Start the serial communication.
        """
        pass

    @abstractmethod
    def has_started(self) -> bool:
        """
        Check if the communication has started.

        Returns:
            bool: True if the communication has started, False otherwise.
        """
        pass

    @abstractmethod
    def receive_message(self) -> IncomingMessage | None:
        """
        Get a message from the incoming messages queue.

        Returns:
            IncomingMessage|None: The message from the incoming messages queue or None if no message is available.
        """
        pass

    @abstractmethod
    def peek_last_received_message(self) -> IncomingMessage | None:
        """
        Peek the last message from the incoming messages queue without removing it.

        Returns:
            Message|None: The last incoming message or None if no message is available.
        """
        pass

    @abstractmethod
    def _send_message(self, msg: OutgoingMessage) -> None:
        """
        Put a message in the outgoing messages queue.

        Args:
            msg (OutgoingMessage): The message to put in the queue.
        """
        pass

    @abstractmethod
    def send_rplidar_measures(self, measures: dict[RPLIDAR, float]) -> None:
        """
        Put RPLIDAR measures in the outgoing messages queue.

        Args:
            measures (dict[RPLIDAR, float]): Dictionary containing RPLIDAR measures to put in the queue.
        """
        pass

    @abstractmethod
    def wait_stop_event(self) -> None:
        """
        Wait for the stop event to be set.
        """
        pass

    @abstractmethod
    def wait_start_event(self) -> None:
        """
        Wait for the start event to be set.
        """
        pass

    @abstractmethod
    def wait_parking_event(self) -> None:
        """
        Wait for the parking event to be set.
        """
        pass

    @abstractmethod
    def wait_pending_incoming_message_event(self) -> None:
        """
        Wait for a pending incoming message event.
        """
        pass

    @abstractmethod
    def wait_pending_outgoing_message_event(self) -> None:
        """
        Wait for a pending outgoing message event.
        """
        pass

    @abstractmethod
    def _receiving_message_handler(self) -> None:
        """
        Handler to receive messages from the serial port.
        """
        pass

    @abstractmethod
    def _sending_message_handler(self) -> None:
        """
        Handler to send messages to the serial port.
        """
        pass