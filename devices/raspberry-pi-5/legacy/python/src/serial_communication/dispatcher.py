from multiprocessing import Queue
from typing import final

from .abstracts import DispatcherABC
from .common_messages import OUTGOING_OK_MESSAGE, STOP_MESSAGE
from .enums import OutgoingCategory
from .message import OutgoingMessage
from ..utils import is_instance


class Dispatcher(DispatcherABC):
	"""
	Class for a dispatcher that handles incoming and outgoing messages.
	"""

	def __init__(
			self,
			serial_messages_queue: Queue,
			) -> None:
		"""
		Initializes the Dispatcher class.

		Args:
			serial_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
		"""
		# Initialize the queue
		self.__serial_messages_queue = serial_messages_queue

	@final
	def _send_message(self, msg: OutgoingMessage) -> None:
		# Check the type of message
		is_instance(msg, OutgoingMessage)

		# Put the message in the queue
		self.__serial_messages_queue.put(msg)

	@final
	def send_motor_speed_message(self, speed: float) -> None:
		# Create the message
		msg = OutgoingMessage(OutgoingCategory.MOTOR_SPEED, str(speed))

		# Send the message
		self._send_message(msg)

	@final
	def send_servo_angle_message(self, angle: float) -> None:
		# Create the message
		msg = OutgoingMessage(OutgoingCategory.SERVO_ANGLE, str(angle))

		# Send the message
		self._send_message(msg)

	@final
	def send_confirmation_message(self) -> None:
		self._send_message(OUTGOING_OK_MESSAGE)

	@final
	def send_stop_message(self) -> None:
		self._send_message(STOP_MESSAGE)
