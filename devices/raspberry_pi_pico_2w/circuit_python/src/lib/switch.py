from asyncio import create_task, gather, sleep

from digitalio import DigitalInOut, Direction, Pull

from .led import LEDHandler
from .serial_communication import SerialCommunication


class SwitchHandler:
	"""
	A class to handle a switch connected to a Raspberry Pi Pico.
	"""
	# Default configuration
	DELAY = 0.01

	def __init__(
			self,
			serial_communication: SerialCommunication,
			switch_pin: int,
			led: LEDHandler = None,
			):
		"""
		Initializes the switch handler with the specified pin.

		Args:
			serial_communication (SerialCommunication): Serial communication handler.
			switch_pin (int): The GPIO number where the switch is connected.
			led (LEDHandler | None): Optional LED handler for visual feedback when the switch is pressed.
		"""
		# Set up the switch pin as input with pull-up resistor
		self.__switch = DigitalInOut(switch_pin)
		self.__switch.direction = Direction.INPUT
		self.__switch.pull = Pull.UP

		# If serial communication is provided, set it
		self.__serial_communication = serial_communication

		# If LED handler is provided, set it
		self.__led = led

	async def wait(self):
		"""
		Waits for the switch to be pressed.

		This method blocks until the switch is pressed (i.e., the pin reads LOW).
		"""
		# Check if the switch is already pressed
		if not self.__switch.value:
			while not self.__switch.value:
				await sleep(self.DELAY)

		while self.__switch.value:
			await sleep(self.DELAY)

		# Send initialization message
		self.__serial_communication.send_initialization_message()

		# Send challenge message
		await self.__serial_communication.send_challenge_message()

		# Create the tasks to signal the start of the robot's operation
		start_tasks = [create_task(self.__serial_communication.start())]

		# Blink the LED if provided
		if self.__led:
			start_tasks.append(create_task(self.__led.blink()))

		# Wait for all start tasks to complete
		await gather(*start_tasks)
