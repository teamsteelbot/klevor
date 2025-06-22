from ..constants import WIDTH, HEIGHT

# Image processing constants
CHANNELS = 3
SHAPE = (HEIGHT, WIDTH, CHANNELS)

# Color
COLOR = (0, 255, 0)

# Padding color
PADDING_COLOR: tuple[int, int, int] = (0, 0, 0)

# Unused color
UNUSED_COLOR = (255, 255, 255)

# Calibration set
MAX_CALIB_SET_SAMPLES = 100

# Number of augmentation samples
AUGMENTATION_SAMPLES = 10