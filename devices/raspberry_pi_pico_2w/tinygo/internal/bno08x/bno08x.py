from asyncio import sleep
from math import (asin, atan2, degrees, pi)

from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)
from adafruit_bno08x.i2c import BNO08X_I2C
from busio import I2C

from .serial_communication import SerialCommunication


class BNO08XError(Exception):
	"""
	Custom exception class for BNO08X errors.
	"""

	def __init__(self, message):
		"""
		Initializes the BNO08XError with a custom message.
		"""
		super().__init__(message)
		self.message = message

	def __str__(self):
		"""
		Returns a string representation of the BNO08XError.
		"""
		return f"BNO08X Error: {self.message}"


class BNO08XHandler:
	"""
	A class to handle BNO08X sensor operations.
	"""
	# Default configuration
	I2C_ADDRESS = 0x4b
	INITIAL_SAMPLES = 10  # Number of samples to gather for initial calibration

	# Delay between readings in seconds
	DELAY = 0.05

	def __init__(
			self,
			i2c: I2C,
			address: int = I2C_ADDRESS,
			serial_communication: SerialCommunication = None,
			is_upside_down: bool = False,
			):
		"""
		Initializes the BNO08X handler with the specified I2C bus and address.

		Args:
			i2c (I2C): The I2C bus to use for communication with the BNO08X sensor.
			address (int): The I2C address of the BNO08X sensor.
			serial_communication (SerialCommunication | None): Optional serial communication handler.
			is_upside_down (bool): If True, the sensor is mounted upside down.
		"""
		# Initialize the I2C bus and BNO08X sensor
		self.__bno = BNO08X_I2C(i2c, address=address)
		self.__bno.enable_feature(BNO_REPORT_GYROSCOPE)
		self.__bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

		# Check the type of serial communication
		self.__serial_communication = serial_communication

		# Check if the sensor is mounted upside down
		self.YAW_FACTOR = -1.0 if is_upside_down else 1.0

		# Set accumulated values to zero
		self.__accumulated_yaw_deg = 0.0
		self.__last_yaw_deg = 0.0
		self.__accumulated_90_deg_turns = 0
		self.__last_segment_count = 0

		# Initialize gyroscope values
		self.__gyro_x_deg, self.__gyro_y_deg, self.__gyro_z_deg = 0.0, 0.0, 0.0

		# Initialize quaternion values
		self.__initial_roll_deg, self.__initial_pitch_deg, self.__initial_yaw_deg = 0.0, 0.0, 0.0
		self.__roll_deg, self.__pitch_deg, self.__yaw_deg = 0.0, 0.0, 0.0

		# Set has been calibrated flag
		self.__calibrated = False

	async def calibrate(self):
		"""
		Calibrates the BNO08X sensor by taking initial readings to set the initial orientation.

		Raises:
			BNO08XError: If the sensor is already calibrated.
		"""
		# Check if already calibrated
		# if self.__calibrated:
		#     raise BNO08XError("BNO08X sensor is already calibrated.")

		# Set the calibrated flag to True
		self.__calibrated = True

		# Gathering multiple samples to fix errors
		for _ in range(self.INITIAL_SAMPLES):
			await self.__read_quaternion()
			await sleep(self.DELAY)

		# Saving the orientation, this makes the turns variables much smoother to handle
		self.__initial_roll_deg, self.__initial_pitch_deg, self.__initial_yaw_deg = BNO08XHandler.quaternion_to_euler_degrees(
			*self.__quaternion,
			)

	@staticmethod
	def quaternion_to_euler_degrees(x: float, y: float, z: float, w: float):
		"""
		This function receives the 4 components of the quaternion and calculates the orientation
		"""
		# Roll
		sinr_cosp = 2 * (w * x + y * z)
		cosr_cosp = 1 - 2 * (x * x + y * y)
		roll_rad = atan2(sinr_cosp, cosr_cosp)

		# Pitch
		sinp = 2 * (w * y - z * x)

		# Clamp the value to avoid domain errors for asin (should be between -1 and 1)
		if sinp > 1:
			pitch_rad = pi / 2
		elif sinp < -1:
			pitch_rad = -pi / 2
		else:
			pitch_rad = asin(sinp)

		# Yaw
		siny_cosp = 2 * (w * z + x * y)
		cosy_cosp = 1 - 2 * (y * y + z * z)
		yaw_rad = atan2(siny_cosp, cosy_cosp)

		return degrees(roll_rad), degrees(pitch_rad), degrees(yaw_rad)

	@staticmethod
	def gyro_to_degrees(x_rad: float, y_rad: float, z_rad: float):
		"""
		Converts gyroscope readings from radians to degrees.
		"""
		return (
			degrees(x_rad),
			degrees(y_rad),
			degrees(z_rad),
			)

	@property
	def quaternion(self):
		"""
		Returns the current quaternion data from the BNO08X sensor.
		"""
		if not hasattr(self, '__quaternion'):
			self.__read_quaternion()
		return self.__quaternion

	@property
	def initial_pitch(self):
		"""
		Returns the initial pitch value in degrees.
		"""
		return self.__initial_pitch_deg

	@property
	def initial_roll(self):
		"""
		Returns the initial roll value in degrees.
		"""
		return self.__initial_roll_deg

	@property
	def initial_yaw(self):
		"""
		Returns the initial yaw value in degrees.
		"""
		return self.__initial_yaw_deg

	@property
	def accumulated_yaw_deg(self):
		"""
		Returns the accumulated yaw degrees value since the last reset.
		"""
		return self.__accumulated_yaw_deg

	@property
	def accumulated_90_deg_turns(self):
		"""
		Returns the accumulated 90-degree turns since the last reset.
		"""
		return self.__accumulated_90_deg_turns

	@property
	def roll(self):
		"""
		Returns the current roll value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__roll_deg'):
			self.update_quaternion()
		return self.__roll_deg

	@property
	def pitch(self):
		"""
		Returns the current pitch value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__pitch_deg'):
			self.update_quaternion()
		return self.__pitch_deg

	@property
	def yaw(self):
		"""
		Returns the current yaw value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__yaw_deg'):
			self.update_quaternion()
		return self.__yaw_deg

	@property
	def gyro(self):
		"""
		Returns the current gyroscope data in radians from the BNO08X sensor.
		"""
		if not hasattr(self, 'gyro'):
			self.__read_gyro()
		return self.__gyro

	@property
	def gyro_x(self):
		"""
		Returns the current gyroscope X value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__gyro_x_deg'):
			self.update_gyro()
		return self.__gyro_x_deg

	@property
	def gyro_y(self):
		"""
		Returns the current gyroscope Y value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__gyro_y_deg'):
			self.update_gyro()
		return self.__gyro_y_deg

	@property
	def gyro_z(self):
		"""
		Returns the current gyroscope Z value in degrees from the BNO08X sensor.
		"""
		if not hasattr(self, '__gyro_z_deg'):
			self.update_gyro()
		return self.__gyro_z_deg

	async def __read_gyro(self):
		"""
		Reads the gyroscope data.
		"""
		self.__gyro = self.__bno.gyro

		# Adding a delay to ensure the sensor has time to update
		await sleep(self.DELAY)

	async def update_gyro(self):
		"""
		Reads the gyroscope data from the BNO08X sensor and updates the gyroscope values in degrees.
		"""
		# Updating the gyroscope data
		await self.__read_gyro()

		# Get the current gyroscope values in degrees
		self.__gyro_x_deg, self.__gyro_y_deg, self.__gyro_z_deg = BNO08XHandler.gyro_to_degrees(
			*self.__gyro,
			)

	async def __read_quaternion(self):
		"""
		Reads the quaternion data from the BNO08X sensor.
		"""
		self.__quaternion = self.__bno.quaternion

		# Adding a delay to ensure the sensor has time to update
		await sleep(self.DELAY)

	async def update_quaternion(self):
		"""
		Reads the quaternion data from the BNO08X sensor and updates the roll, pitch, and yaw values.
		"""
		# Updating the quaternion data
		await self.__read_quaternion()

		# Get the current roll, pitch, and yaw in degrees
		self.__roll_deg, self.__pitch_deg, self.__yaw_deg = BNO08XHandler.quaternion_to_euler_degrees(
			*self.__quaternion,
			)

		# If serial communication is enabled, send the yaw degrees message
		if self.__serial_communication:
			self.__serial_communication.send_bno08x_yaw_deg_message(
				self.__yaw_deg,
				)

		# Compute relative yaw degrees
		relative_yaw_deg = self.__yaw_deg - self.__initial_yaw_deg
		if relative_yaw_deg > 180:
			relative_yaw_deg -= 360
		elif relative_yaw_deg < -180:
			relative_yaw_deg += 360

		# Calculate the change in yaw degrees since the last update
		delta_raw_yaw_deg = relative_yaw_deg - self.__last_yaw_deg
		if delta_raw_yaw_deg > 180:
			delta_raw_yaw_deg -= 360
		elif delta_raw_yaw_deg < -180:
			delta_raw_yaw_deg += 360

		# Update accumulated yaw and segment count
		self.__accumulated_yaw_deg += delta_raw_yaw_deg
		current_segment_count = int(self.__accumulated_yaw_deg / 90)
		if current_segment_count != self.__last_segment_count:
			self.__accumulated_90_deg_turns += current_segment_count - self.__last_segment_count
			self.__last_segment_count = current_segment_count

			# If serial communication is enabled, send the turn message
			if self.__serial_communication:
				self.__serial_communication.send_bno08x_turns_message(
					abs(self.__accumulated_90_deg_turns),
					)

		self.__last_yaw_deg = relative_yaw_deg

	@property
	def turns(self):
		"""
		Returns the number of 90-degree turns made since the last reset.
		"""
		return self.__accumulated_90_deg_turns
