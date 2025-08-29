from multiprocessing import Event, Queue, RLock
from multiprocessing.synchronize import Event as EventCls
from queue import Empty
from typing import TextIO, final

from .abstracts import WriterABC
from .enums import Category
from .message import Message
from ..files import Files
from ..utils import is_instance
from ..utils.decorators import ignore_sigint


class Writer(WriterABC):
	"""
	Class to handle writing log messages to a file.
	"""

	# Wait timeout for processing messages
	WAIT_TIMEOUT = 0.1

	def __init__(
			self,
			debug: bool,
			messages_queue: Queue,
			stop_event: EventCls,
			) -> None:
		"""
		Initialize the Logger class.

		Args:
			debug (bool): Flag to indicate if the logger is in debug mode.
			messages_queue (Queue): Queue to hold log messages.
			stop_event (EventCls): Event to signal when the logger should stop.
		"""
		# Initialize the debug flag
		self.__debug = debug

		# Initialize the messages queue and events
		self.__messages_queue = messages_queue
		self.__started_event = Event()
		self.__deleted_event = Event()
		self.__stop_event = stop_event

		# Initialize the reentrant lock
		self.__rlock = RLock()

		# Initialize the file path and file
		self.__file_path: str = ""
		self.__file: TextIO | None = None

	@final
	def _write_last_message(self) -> None:
		try:
			# Process any remaining messages in the queue
			msg = self.__messages_queue.get(timeout=self.WAIT_TIMEOUT)

		except Empty:
			return None

		# Check if the message is an instance of Message
		is_instance(msg, Message)

		# Write the message to the log file
		if not self.__file:
			raise RuntimeError("Log file is not open. Must open it first.")
		self._write(self.__file, msg)

	@final
	def _start(self) -> None:
		with self.__rlock:
			# Check if the stop event is set
			if self.__stop_event.is_set():
				raise RuntimeError("Stop event is set. Logger will not run.")

			# Check if the logger is already running
			if self.__started_event.is_set():
				raise RuntimeError(
					"Logger is already running. Cannot start again.",
					)

			# Set the started event
			self.__started_event.set()

		# Log
		print("Writer initialized.")

	@final
	def _stop(self) -> None:
		# Check if there are any remaining messages in the queue
		while not self.__messages_queue.empty():
			self._write_last_message()

		with self.__rlock:
			# Clear the started event
			self.__started_event.clear()

			# Clear the deleted event
			self.__deleted_event.clear()

		# Write the stop message to the log file
		self._write(self.__file, Message("Writer stopped.", Category.DEBUG))

	@final
	@ignore_sigint
	def run(self, file_path: str = Files.get_log_file_path()) -> None:
		try:
			# Check the type of file_path
			is_instance(file_path, str)
			self.__file_path = file_path

			# Ensure the file exists
			Files.ensure_file_exists(self.__file_path)

			# Start the writer
			self._start()

		except Exception as e:
			print(f"An error occurred while starting the Writer: {e}")
			raise e

		try:
			# Open the log file in append mode
			print(f"Opening log file at {self.__file_path}...")
			with open(self.__file_path, 'a') as file:
				# Set the file
				self.__file = file

				# Process messages from the queue
				while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
					# Write the last message if available
					self._write_last_message()

				# Stop the writer
				self._stop()

		except Exception as e:
			# Stop the writer in case of an exception
			self._stop()

			# Log any exceptions that occur
			print(f"An error occurred while running the Writer: {e}")
			raise e

	def __del__(self):
		"""
		Destructor to clean up resources when the photographer is no longer needed.
		"""
		self.__deleted_event.set()

		# Log
		print("Writer instance is being deleted. Resources will be cleaned up.")
