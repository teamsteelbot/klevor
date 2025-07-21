from time import sleep

from adafruit_vl53l0x import VL53L0X
from busio import I2C
from digitalio import DigitalInOut, Direction


class VL53L0XError(Exception):
	"""
	Custom exception class for VL53L0X errors.
	"""

	def __init__(self, message):
		"""
		Initializes the VL53L0XError with a custom message.
		"""
		super().__init__(message)
		self.message = message

	def __str__(self):
		"""
		Returns a string representation of the VL53L0XError.
		"""
		return f"VL53L0X Error: {self.message}"


class VL53L0XHandler:
	"""
	This class handles the initialization and reading of multiple VL53L0X ToF sensors.
	"""
	# Default configuration
	SHORT_SETUP_DELAY = 0.05  # Short delay for sensor power-up
	SETUP_DELAY = 0.1  # Delay to ensure all sensors are off before starting
	MEASUREMENT_LIMIT_MM = 3000  # Maximum distance for ToF measurement in mm
	MEASUREMENT_TIMING_BUDGET = 100000  # Timing budget for ToF measurement in microseconds
	SENSOR_DELAY = 0.05
	START_NEW_I2C_ADDRESS = 0x30

	def __init__(
			self,
			i2c: I2C,
			xshut_pins: tuple[int, ...],
			):
		"""
		Initializes the VL53L0XHandler with default settings.

		Args:
			i2c (I2C): The I2C bus instance to communicate with the sensors.
			xshut_pins (tuple): A tuple of GPIO pins used to control the XSHUT lines of the sensors.

		Raises:
			VL53L0XError: If there is an error initializing the sensors.
		"""
		# Initialize XSHUT list, sensors and measures list
		self.__xshut = []
		self.__sensors = []
		self.__sensors_measures = [None for _ in range(len(xshut_pins))]

		# Fill the XSHUT list with DigitalInOut objects for each pin
		for i, pin in enumerate(xshut_pins):
			xshut = DigitalInOut(pin)
			xshut.direction = Direction.OUTPUT
			xshut.value = False
			self.__xshut.append(xshut)
			sleep(self.SETUP_DELAY)

			try:
				# Initialize the sensor, should be at 0x29
				sensor = VL53L0X(i2c)

				# Change the I2C address of the current sensor to a new unique address
				sensor.set_address(self.START_NEW_I2C_ADDRESS + i)
				self.__sensors.append(sensor)

				# Set the ToF measurement timing budget
				sensor.measurement_timing_budget = self.MEASUREMENT_TIMING_BUDGET

				# Small synchronous pause before activating next sensor
				sleep(self.SHORT_SETUP_DELAY)

			except ValueError as e:
				raise VL53L0XError(
					f"Failed to initialize sensor on pin {pin}: {e}",
					)

	async def multiple_tof_sensors_reading(self):
		"""
		Asynchronously reads the distance from multiple VL53L0X ToF sensors.

		Raises:
			VL53L0XError: If there is an error reading from any sensor.
		"""
		for i, sensor in enumerate(self.__sensors):
			try:
				# Read the distance from the sensor
				distance_mm = sensor.range
				if distance_mm is None or distance_mm < 0:
					pass
				if distance_mm >= self.MEASUREMENT_LIMIT_MM:
					distance_cm = float('inf')
				else:
					distance_cm = distance_mm // 10  # Convert to centimeters

				# Store the distance in the measures list
				self.__sensors_measures[i] = distance_cm

				sleep(self.SENSOR_DELAY)

			except Exception as e:
				raise VL53L0XError(
					f"Error reading sensor on pin {self.__xshut[i].pin}: {e}",
					)
