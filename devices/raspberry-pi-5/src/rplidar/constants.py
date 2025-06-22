import os

# RPLIDAR C1 baud rate
RPLIDAR_C1_BAUDRATE = 460800

# Default port
RPLIDAR_C1_PORT = "/dev/ttyUSB0"

# Max distance limit
MAX_DISTANCE_LIMIT = 3000

# Distance difference
DISTANCE_DIFF = 25

# Get the absolute path of the ultra_simple executable
ULTRA_SIMPLE_PATH = os.path.join(os.path.dirname(__file__), "ultra_simple")