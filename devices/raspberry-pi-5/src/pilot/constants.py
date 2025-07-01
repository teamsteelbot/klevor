from .enums import Direction

# Motor speed range
MOTOR_SPEED_RANGE = (-1.0, 1.0)

# Common motor speed values
MOTOR_SPEED_FAST = 0.6
MOTOR_SPEED_NORMAL = 0.45
MOTOR_SPEED_SLOW = 0.3

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
FRONT_DISTANCE_THRESHOLD = 500.0
SIDE_DISTANCE_DIFFERENCE_PERCENTAGE = 0.2
SIDE_DISTANCE_THRESHOLD = 1500.0
STOP_DISTANCE_THRESHOLD = 1500.0
TARGET_DISTANCE_STOP_START = 2000.0
SAFETY_FRONT_DISTANCE_THRESHOLD = 150.0

# Angle widths
ANGLE_WIDTH = 5

# Map directions to angles
DIRECTION_TO_ANGLE = {
    Direction.NORTH: 0,
    Direction.NORTH_NORTHEAST: 22.5,
    Direction.NORTHEAST: 45,
    Direction.EAST_NORTHEAST: 67.5,
    Direction.EAST: 90,
    Direction.EAST_SOUTHEAST: 112.5,
    Direction.SOUTHEAST: 135,
    Direction.SOUTHWEST: 225,
    Direction.WEST_SOUTHWEST: 247.5,
    Direction.WEST: 270,
    Direction.WEST_NORTHWEST: 292.5,
    Direction.NORTHWEST: 315,
    Direction.NORTH_NORTHWEST: 337.5,
}