 import os

# RPLidar C1 baud rate
RPLIDAR_C1_BAUDRATE = 460800

# RPLidar C1 default port
RPLIDAR_C1_PORT = "/dev/ttyUSB0"

# Max distance limit
MAX_DISTANCE_LIMIT = 3000

# Distance difference
DISTANCE_DIFF = 25

# Apps folder
APPS_DIR = os.path.join(os.path.dirname(__file__), "apps")

# Get the absolute path of the ultra_simple executable
ULTRA_SIMPLE_PATH = os.path.join(APPS_DIR, "ultra_simple")
