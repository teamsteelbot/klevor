from board import GP0, GP1
from busio import I2C
from math import (degrees, atan2, asin, pi)
from time import sleep
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)

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
    I2C_SDA_PIN = GP0
    I2C_SCL_PIN = GP1
    I2C_ADDRESS = 0x4B
    DELAY = 0.05
    INITIAL_SAMPLES = 10 # Number of samples to gather for initial calibration

    def __init__(self, i2c: I2C = I2C(I2C_SCL_PIN, I2C_SDA_PIN), address: int = I2C_ADDRESS):
        """
        Initializes the BNO08X handler with the specified I2C bus and address.
        """
        self.__bno = BNO08X_I2C(i2c, address=address)
        self.__bno.enable_feature(BNO_REPORT_GYROSCOPE)
        self.__bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

        # Gathering multiple samples to fix errors
        for _ in range(self.INITIAL_SAMPLES):
            self.__read_quaternion()
            sleep(self.DELAY)

        # Saving the orientation, this makes the turns variables much smoother to handle
        self.__initial_roll_deg, self.__initial_pitch_deg, self.__initial_yaw_deg = self.__quaternion_to_euler_degrees(*self.__quaternion)

        # Set accumulated values to zero
        self.__accumulated_yaw_deg = 0.0
        self.__last_yaw_deg = 0.0
        self.__accumulated_90_deg_turns = 0
        self.__last_segment_count = 0

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
    def accumulated_yaw(self):
        """
        Returns the accumulated yaw value in degrees since the last reset.
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

    def __gyro_to_degrees(self, x_rad: float, y_rad: float, z_rad: float):
        """
        Converts gyroscope readings from radians to degrees.
        """
        return (
            degrees(x_rad),
            degrees(y_rad),
            degrees(z_rad)
        )

    def __quaternion_to_euler_degrees(self, x: float, y: float, z: float, w: float):
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

    def __read_gyro(self):
        """
        Reads the gyroscope data.
        """
        self.__gyro = self.__bno.gyro

        # Adding a delay to ensure the sensor has time to update
        sleep(self.DELAY)

    def update_gyro(self):
        """
        Reads the gyroscope data from the BNO08X sensor and updates the gyroscope values in degrees.
        """
        # Updating the gyroscope data
        self.__read_gyro()

        # Get the current gyroscope values in degrees
        self.__gyro_x_deg, self.__gyro_y_deg , self.__gyro_z_deg = self.__gyro_to_degrees(*self.__gyro)

    def __read_quaternion(self):
        """
        Reads the quaternion data from the BNO08X sensor.
        """
        self.__quaternion = self.__bno.quaternion

        # Adding a delay to ensure the sensor has time to update
        sleep(self.DELAY)

    def update_quaternion(self):
        """
        Reads the quaternion data from the BNO08X sensor and updates the roll, pitch, and yaw values.
        """
        # Updating the quaternion data
        self.__read_quaternion()

        # Get the current roll, pitch, and yaw in degrees
        self.__roll_deg, self.__pitch_deg, self.__yaw_deg = self.__quaternion_to_euler_degrees(*self.__quaternion)

        # Compute relative yaw
        relative_yaw = self.__yaw_deg - self.__initial_yaw_deg
        if relative_yaw > 180:
            relative_yaw -= 360
        elif relative_yaw < -180:
            relative_yaw += 360

        # Calculate the change in yaw since the last update
        delta_raw_yaw = relative_yaw - self.__last_yaw_deg
        if delta_raw_yaw > 180:
            delta_raw_yaw -= 360
        elif delta_raw_yaw < -180:
            delta_raw_yaw += 360

        # Update accumulated yaw and segment count
        self.__accumulated_yaw_deg += delta_raw_yaw
        current_segment_count = int(self.__accumulated_yaw_deg / 90)
        if current_segment_count != self.__last_segment_count:
            self.__accumulated_90_deg_turns += current_segment_count - self.__last_segment_count
            self.__last_segment_count = current_segment_count

        self.__last_yaw_deg = relative_yaw
