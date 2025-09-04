from .enums import CardinalDirection

# Motor speed range
MOTOR_SPEED_RANGE = (-1.0, 1.0)

# Common motor speed values
MOTOR_SPEED_FAST = 0.65
MOTOR_SPEED_NORMAL = 0.5
MOTOR_SPEED_SLOW = 0.4

# Servo center angle
SERVO_CENTER_ANGLE = 75

# Servo actuation range
SERVO_ACTUATION_RANGE = 180
SERVO_LEFT_LIMIT = -(SERVO_ACTUATION_RANGE - SERVO_CENTER_ANGLE)
SERVO_RIGHT_LIMIT = (SERVO_ACTUATION_RANGE - (SERVO_ACTUATION_RANGE -
                                              SERVO_CENTER_ANGLE))

# Servo angles for different turns
SERVO_BIG_TURN_ANGLE = 35
SERVO_MEDIUM_TURN_ANGLE = 25
SERVO_SMALL_TURN_ANGLE = 20

# Maximum number of turns in the algorithm
TURNS = 12

# Distance constants
FRONT_START_TURN_DISTANCE_THRESHOLD = 600.0  # 500.0
FRONT_STOP_TURN_DISTANCE_THRESHOLD = 1500.0
SIDE_DISTANCE_DIFFERENCE_PERCENTAGE = 0.15  # 0.2
SIDE_DISTANCE_THRESHOLD = 1500.0
STOP_DISTANCE_THRESHOLD = 1500.0
SAFETY_FRONT_DISTANCE_START_THRESHOLD = 200.0
SAFETY_FRONT_DISTANCE_STOP_THRESHOLD = 350.0

# Angle widths
ANGLE_WIDTH = 5

# Map directions to angles
DIRECTION_TO_ANGLE = {
	CardinalDirection.NORTH: 0,
	CardinalDirection.NORTH_NORTHEAST: 22.5,
	CardinalDirection.NORTHEAST: 45,
	CardinalDirection.EAST_NORTHEAST: 67.5,
	CardinalDirection.EAST: 90,
	CardinalDirection.EAST_SOUTHEAST: 112.5,
	CardinalDirection.SOUTHEAST: 135,
	CardinalDirection.SOUTH_SOUTHEAST: 157.5,
	CardinalDirection.SOUTH: 180,
	CardinalDirection.SOUTH_SOUTHWEST: 202.5,
	CardinalDirection.SOUTHWEST: 225,
	CardinalDirection.WEST_SOUTHWEST: 247.5,
	CardinalDirection.WEST: 270,
	CardinalDirection.WEST_NORTHWEST: 292.5,
	CardinalDirection.NORTHWEST: 315,
	CardinalDirection.NORTH_NORTHWEST: 337.5,
	}
