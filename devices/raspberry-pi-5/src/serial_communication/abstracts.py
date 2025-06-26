from abc import ABC, abstractmethod

from .message import IncomingMessage, OutgoingMessage
from ..log import Logger


class SerialCommunicationABC(ABC):
    """
    Abstract class to handle the serial communication through USB.
    """

    @property
    @abstractmethod
    def logger(self) -> Logger:
        """
        Get the logger instance for the SerialCommunication.

        Returns:
            Logger: The logger instance.
        """
        pass

    @abstractmethod
    def _start(self) -> None:
        """
        Start the serial communication.

        Raises:
            RuntimeError: If the serial port cannot be opened.
        """
        pass

    @abstractmethod
    def _stop(self) -> None:
        """
        Stop the serial communication.
        """
        pass

    @abstractmethod
    def _receive_latest_message(self, readline: bool = True) -> (
            IncomingMessage | None):
        """
        Receive the latest message from the serial port.

        Args:
            readline (bool): If True, read the message line by line.
                             If False, read the message as a whole.
        Returns:
            IncomingMessage | None: The latest incoming message or None if no message is available.
        """
        pass

    @abstractmethod
    def _send_latest_message(self) -> None:
        """
        Sends the latest message from the outgoing messages queue.
        """
        pass

    @abstractmethod
    def _send_confirmation_message(self) -> None:
        """
        Send a confirmation message to the serial port.
        """
        pass

    @abstractmethod
    def _wait_confirmation_message(
        self,
        msg_to_confirm: OutgoingMessage
    ) -> None:
        """
        Wait for the confirmation message from the serial port.

        Args:
            msg_to_confirm (OutgoingMessage): The message to confirm.
        Raises:
            RuntimeError: If an error message is received instead of a confirmation message or if the confirmation message is not received within a timeout.
        """
        pass

    @abstractmethod
    def _send_stop_message(self) -> None:
        """
        Send a stop message to the serial port.
        """
        pass

    @abstractmethod
    def _receiving_message_handler(self) -> None:
        """
        Handler to receive messages from the serial port.

        Raises:
            RuntimeError: If an error message is received or if the confirmation message is not received within a timeout.
        """
        pass

    @abstractmethod
    def _sending_message_handler(self) -> None:
        """
        Handler to send messages to the serial port.
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
        Run the serial communication by creating threads for receiving and sending messages.
        """
        pass


class DispatcherABC:
    """
    Abstract class for a dispatcher that handles incoming and outgoing messages.
    """

    @abstractmethod
    def receive_message(self) -> IncomingMessage | None:
        """
        Get a message from the incoming messages queue.

        Returns:
            IncomingMessage|None: The message from the incoming messages queue or None if no message is available.
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
    def send_motor_speed_message(self, speed: float) -> None:
        """
        Send the motor speed to the serial port.

        Args:
            speed (float): The speed of the motor.
        """
        pass

    @abstractmethod
    def send_servo_angle_message(self, angle: float) -> None:
        """
        Send the servo angle to the serial port.

        Args:
            angle (float): The angle of the servo.
        """
        pass

    @abstractmethod
    def send_stop_message(self) -> None:
        """
        Send a stop message to the serial port.
        """
        pass
