import os

# Root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Image dimensions
WIDTH = 640
HEIGHT = 640

# Image size
SIZE = 640

# Imae format
IMAGE_FORMAT = 'jpeg'

# Colors
GREEN_COLOR = (68, 214, 44)
MAGENTA_COLOR = (255, 0, 255)
RED_COLOR = (238, 39, 55)

# YOLO model names
MODEL_M = 'm'
MODEL_G = 'g'
MODEL_R = 'r'
MODELS_NAME = (MODEL_M, MODEL_G, MODEL_R)

# YOLO class colors
MODEL_G_COLORS = (GREEN_COLOR,)
MODEL_M_COLORS = (MAGENTA_COLOR,)
MODEL_R_COLORS = (RED_COLOR,)
MODELS_COLORS = {
    MODEL_G: MODEL_G_COLORS,
    MODEL_M: MODEL_M_COLORS,
    MODEL_R: MODEL_R_COLORS,
}

# YOLO model versions
VERSION_11 = 'v11'
VERSIONS = (VERSION_11,)