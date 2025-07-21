import io
from multiprocessing import Queue
from typing import final

from PIL.Image import Image

from .abstracts import DispatcherABC
from ..common.measure import Measure
from ..constants import IMAGE_FORMAT, MODEL_G, MODEL_M, MODEL_R
from ..log import Logger
from ..server.enums import Tag
from ..server.message import Message
from ..utils import is_instance


class Dispatcher(DispatcherABC):
	"""
	Class for a dispatcher that handles broadcasting messages and images
	"""

	# Logger configuration
	LOGGER_TAG = "Dispatcher"

	def __init__(
			self,
			server_messages_queue: Queue,
			writer_messages_queue: Queue,
			):
		"""
		Initializes the Dispatcher class.

		Args:
			server_messages_queue (Queue): Queue to broadcast messages through the websockets server.
			writer_messages_queue (Queue): Queue to hold log messages.
		"""
		# Initialize the server messages queue
		self.__server_messages_queue = server_messages_queue

		# Initialize the logger
		self.__logger = Logger(
			writer_messages_queue, self.LOGGER_TAG,
			unique_tag=True,
			)

	@final
	def _broadcast_message(self, msg: Message):
		# Check the type of message
		is_instance(msg, Message)

		# Put the message in the server messages queue
		self.__server_messages_queue.put(msg)

	@final
	def _broadcast_image_with_tag(self, tag: Tag, img: Image):
		try:
			# Open the image and convert it to a binary stream
			img_stream = io.BytesIO()
			img.save(img_stream, format=IMAGE_FORMAT)
			img_stream.seek(0)
			binary_data = img_stream.read()

			# Send the tagged binary data to the clients
			self._broadcast_message(Message(tag, str(binary_data)))

		except Exception as e:
			self.__logger.error(
				f"Error sending image: {e}",
				) if self.__logger else None

	@final
	def broadcast_original_image(self, img: Image):
		"""
		Broadcasts the original image to all connected clients.
		"""
		self._broadcast_image_with_tag(Tag.IMAGE_ORIGINAL, img)

	def _broadcast_model_g_image(self, img: Image):
		"""
		Broadcasts the image processed by model G to all connected clients.
		"""
		self._broadcast_image_with_tag(Tag.IMAGE_MODEL_G, img)

	def _broadcast_model_m_image(self, img: Image):
		"""
		Broadcasts the image processed by model M to all connected clients.
		"""
		self._broadcast_image_with_tag(Tag.IMAGE_MODEL_M, img)

	def _broadcast_model_r_image(self, img: Image):
		"""
		Broadcasts the image processed by model R to all connected clients.
		"""
		self._broadcast_image_with_tag(Tag.IMAGE_MODEL_R, img)

	@final
	def broadcast_model_image(self, img: Image, model_name: str):
		# Check the type of model_name
		is_instance(model_name, str)

		# Check the type of image
		is_instance(img, Image)

		if model_name == MODEL_G:
			self._broadcast_model_g_image(img)

		elif model_name == MODEL_M:
			self._broadcast_model_m_image(img)

		elif model_name == MODEL_R:
			self._broadcast_model_r_image(img)

		else:
			raise ValueError(f"Unknown model name: {model_name}")

	@final
	def broadcast_serial_incoming_message(self, msg: str):
		# Check the type of msg
		is_instance(msg, str)

		# Send a tagged message
		self._broadcast_message(Message(Tag.SERIAL_INCOMING_MESSAGE, msg))

	@final
	def broadcast_serial_outgoing_message(self, msg: str):
		# Check the type of msg
		is_instance(msg, str)

		# Send a tagged message
		self._broadcast_message(Message(Tag.SERIAL_OUTGOING_MESSAGE, msg))

	@final
	def broadcast_rplidar_measure(self, measure: Measure):
		# Check the type of measure
		is_instance(measure, Measure)

		# Send a tagged message
		self._broadcast_message(Message(Tag.RPLIDAR_MEASURES, str(measure)))
