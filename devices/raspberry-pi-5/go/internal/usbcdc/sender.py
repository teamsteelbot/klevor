from multiprocessing import Event, RLock
from multiprocessing.synchronize import Event as EventCls
from queue import Empty, Queue
from time import sleep
from typing import Optional, final

from serial import Serial

from .abstracts import SenderABC
from .common_messages import (
	HEARTBEAT_MESSAGE,
	OUTGOING_OK_MESSAGE,
	STOP_MESSAGE,
	)
from .constants import (
	ATTEMPTS_DELAY,
	CONNECTION_ATTEMPTS,
	ENCODE,
	END_CHAR,
	RASPBERRY_PI_PICO_BAUDRATE,
	RASPBERRY_PI_PICO_DATA_PORTS,
	STOP_TIMEOUT,
	)
from .message import OutgoingMessage
from ..log import Logger
from ..log.decorators import LoggerConsumerProtocol, log_on_error
from ..server.dispatcher import Dispatcher as ServerDispatcher
from ..utils import is_instance


class Sender(SenderABC, LoggerConsumerProtocol):
	"""
	Sender class to handle serial communication with the Raspberry Pi Pico.
	"""

	# Logger configuration
	LOGGER_TAG = "SerialCommunicationSender"

	# Outgoing wait timeout
	OUTGOING_WAIT_TIMEOUT = 0.1

	# Write timeout
	WRITE_TIMEOUT = 0.5

	def __init__(
			self,
			debug: bool,
			start_event: EventCls,
			stop_sent_event: EventCls,
			stop_confirmation_event: EventCls,
			stop_event: EventCls,
			messages_queue: Queue,
			writer_messages_queue: Queue,
			server_messages_queue: Optional[Queue] = None,
			data_ports: Optional[list[str]] = RASPBERRY_PI_PICO_DATA_PORTS,
			baudrate: Optional[int] = RASPBERRY_PI_PICO_BAUDRATE,
			):
		"""
		Initialize the Receiver class.

		Args:
			debug (bool): Flag to indicate if the receiver is in debug mode.
			start_event (EventCls): Event to signal when the serial communication has started.
			stop_sent_event (EventCls): Event to signal when the stop message has been sent.
			stop_confirmation_event (EventCls): Event to signal when stop messages has been confirmed.
			stop_event (EventCls): Event to signal when the serial communication should stop sending and receiving messages.
			messages_queue (Queue): Queue to hold outgoing messages of the serial port.
			writer_messages_queue (Queue): Queue to hold log messages.
			server_messages_queue (Optional[Queue]): Queue to broadcast the messages through the websockets server.
			data_ports (Optional[list[str]]): List of serial ports used for sending data to Pico.
			baudrate (Optional[int]): Baud rate for the serial communication.
		"""
		# Initialize the debug flag
		self.__debug = debug

		# Initialize the queues and events
		self.__start_event = start_event
		self.__started_event = Event()
		self.__stop_event = stop_event
		self.__stop_sent_event = stop_sent_event
		self.__stop_confirmation_event = stop_confirmation_event
		self.__deleted_event = Event()
		self.__messages_queue = messages_queue

		# Initialize the logger
		self.__logger = Logger(
			writer_messages_queue,
			tag=self.LOGGER_TAG,
			debug=self.__debug,
			)

		# Initialize the server dispatcher
		self.__server_dispatcher = ServerDispatcher(
			server_messages_queue,
			writer_messages_queue,
			) if server_messages_queue else None

		# Initialize the reentrant lock
		self.__rlock = RLock()

		# Check the type of data ports
		is_instance(data_ports, list)
		self.__data_ports = data_ports

		# Check the type of baudrate
		is_instance(baudrate, int)
		self.__baudrate = baudrate

		# Initialize the data serial port
		self.__data_port = None
		self.__data_serial = None

	@final
	def _open_port(self, port: str) -> None:
		try:
			# Create a new Serial instance for the data port
			self.__data_serial = Serial(
				port,
				self.__baudrate,
				write_timeout=self.WRITE_TIMEOUT,
				)
			self.__data_port = port
			self.__data_serial.flush()

		except Exception as e:
			raise RuntimeError(f"Error opening data {port}: {e}")

	@final
	def _start(self) -> None:
		with self.__rlock:
			# Check if the stop event is set
			if self.__stop_event.is_set():
				raise RuntimeError(
					"Stop event is set. Serial communication sender will not run.",
					)

			# Check if the serial communication sender is already running
			if self.__started_event.is_set():
				raise RuntimeError(
					"Serial communication sender is already running. Cannot start again.",
					)

			# Set the started event
			self.__started_event.set()

		# Open the data port
		for i in range(CONNECTION_ATTEMPTS):
			for port in self.__data_ports:
				try:
					self._open_port(port)

					# Log
					self.__logger.info(
						f"Data port opened on {self.__data_port} after {i + 1} {'attempts' if i != 0 else 'attempt'}.",
						)
					return

				except Exception:
					pass

			sleep(ATTEMPTS_DELAY)

		raise RuntimeError(
			f"Failed to open data port after {CONNECTION_ATTEMPTS} attempts.",
			)

	@final
	def _stop(self) -> None:
		with self.__rlock:
			try:
				# Check if the start event is set
				if self.__started_event.is_set():
					# Clear the started event
					self.__started_event.clear()

					# Send the message to the serial port
					self._send_message(STOP_MESSAGE)

					# Set the stop sent event
					self.__stop_sent_event.set()

					# Wait for the confirmation message
					if not self.__stop_confirmation_event.wait(
							timeout=STOP_TIMEOUT,
							):
						self.__logger.warning(
							"Stop confirmation event not set within the timeout.",
							)
					else:
						self.logger.info(
							"Stop confirmation event set.",
							)

					# Clear the stop confirmation event
					self.__stop_confirmation_event.clear()

			except Exception as e:
				# Log the error
				self.__logger.error(
					f"Error while stopping the serial communication sender: {e}",
					)

			# Set the stop event
			self.__stop_event.set()

			# Clear the deleted event
			self.__deleted_event.clear()

			# Close the data serial port
			if self.__data_serial and self.__data_serial.is_open:
				self.__logger.info(
					f"Closing data serial port: {self.__data_port}",
					)
				self.__data_serial.close()
				self.__data_serial = None

		# Log
		self.__logger.info("Stopped.")

	def _send_message(
			self,
			msg: OutgoingMessage,
			) -> None:
		# Log
		msg_str = str(msg)
		self.__logger.debug(
			f"Sending message: {msg_str}",
			)

		# Send the message to the serial port
		self.__data_serial.write(msg_str.encode(ENCODE))

		# Flush the serial port to ensure the message is sent
		self.__data_serial.flush()

	@final
	def _send_confirmation_message(self) -> None:
		self._send_message(OUTGOING_OK_MESSAGE)

	@final
	def _send_latest_message(self) -> OutgoingMessage | None:
		try:
			# Get the message from the queue
			msg = self.__messages_queue.get(
				timeout=self.OUTGOING_WAIT_TIMEOUT,
				)

		except Empty:
			# Sent heartbeat message if the queue is empty
			if self.__start_event.is_set():
				self._send_message(HEARTBEAT_MESSAGE)
			return None

		# Send the message to the serial port
		self._send_message(msg)

		# If the server is set, send the message to the server
		self.__server_dispatcher.broadcast_serial_outgoing_message(
			str(msg).split(END_CHAR, 1)[0],
			) if self.__server_dispatcher else None

	@final
	@log_on_error()
	def run(self) -> None:
		try:
			# Start the serial communication sender
			self._start()

			while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
				self._send_latest_message()

			# Stop
			self._stop()

		except Exception as e:
			# Stop the serial communication in case of an exception
			self._stop()
			raise e

	def __del__(self) -> None:
		"""
		Destructor to clean up resources when the sender is no longer needed.
		"""
		# Set the deleted event
		self.__deleted_event.set()

		# Log the deletion
		self.__logger.info(
			"Instance will be deleted. Resources will be cleaned up.",
			)
