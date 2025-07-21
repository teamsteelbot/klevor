from abc import ABC, abstractmethod

from .message import IncomingMessage, OutgoingMessage
from ..log import Logger


class SerialCommunicationABC(ABC):
	"""
	Abstract class to handle the serial communication through USB.
	"""

	@abstractmethod
	def logger(self) -> Logger:
		"""
		Get the logger instance for the SerialCommunication.

		Returns:
			Logger: The logger instance.
		"""
		pass

	@abstractmethod
	def run(self) -> None:
		"""
		Run the serial communication by creating threads for receiving and sending messages.
		"""
		pass


class ReceiverABC(ABC):
	"""
	Receiver abstract class to handle serial communication with the Raspberry Pi Pico.
	"""

	@abstractmethod
	def logger(self) -> Logger:
		"""
		Get the logger instance for the Receiver.

		Returns:
			Logger: The logger instance.
		"""
		pass

	@abstractmethod
	def _open_port(self, port: str) -> None:
		"""
		Open the console port for communication.

		Args:
			port (str): The console port to open.
		Raises:
			RuntimeError: If the console port cannot be opened.
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
	def _receive_latest_message(self) -> IncomingMessage | None:
		"""
		Receive the latest message from the serial port.

		Returns:
			IncomingMessage | None: The latest incoming message or None if no message is available.
		"""
		pass

	@abstractmethod
	def run(self) -> None:
		"""
		Handler to receive messages from the serial port.

		Raises:
			RuntimeError: If an error message is received or if the confirmation message is not received within a timeout.
		"""
		pass


class SenderABC(ABC):
	"""
	Sender abstract class to handle sending messages through serial communication.
	"""

	@abstractmethod
	def logger(self) -> Logger:
		"""
		Get the logger instance for the Sender.

		Returns:
			Logger: The logger instance.
		"""
		pass

	@abstractmethod
	def _open_port(self, port: str) -> None:
		"""
		Open the data port for serial communication.

		Args:
			port (str): The data port to open.
		Raises:
			RuntimeError: If the data port cannot be opened.
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
	def run(self) -> None:
		"""
		Handler to send messages to the serial port.

		Raises:
			RuntimeError: If an error occurs while sending a message or if the confirmation message is not received within a timeout.
		"""
		pass


class DispatcherABC:
	"""
	Abstract class for a dispatcher that handles incoming and outgoing messages.
	"""

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
	def send_confirmation_message(self) -> None:
		"""
		Send a confirmation message to the serial port.
		"""
		pass

	@abstractmethod
	def send_stop_message(self) -> None:
		"""
		Send a stop message to the serial port.
		"""
		pass
