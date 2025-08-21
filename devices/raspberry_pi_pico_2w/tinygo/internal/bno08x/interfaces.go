package bno08x

type (
	// Handler is the interface for the BNO08x sensor.
	Handler interface {
		Calibrate() error
		readGyroscope() error
		readQuaternion() error
		UpdateQuaternion() error
		Turns() int
	}
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
pitch_rad = -pi / 2 else:
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
