import os

# YOLO folder
YOLO_DIR = os.path.abspath(os.path.dirname(__file__))

# ONNX metadata properties class names key
ONNX_METADATA_CLASS_NAMES_KEY = 'names'

# Number of augmentations
NUM_AUGMENTATIONS = 10

# Epochs
EPOCHS = 100

# Minimum confidence level and number of random images to test
MINIMUM_CONFIDENCE_LEVEL = 0.70
NUMBER_RANDOM_IMAGES = 10

# YOLO formats
FORMAT_ONNX = 'onnx'
FORMAT_TFLITE = 'tflite'
FORMAT_TENSOR_RT = 'tensor_rt'
FORMAT_PT = 'pt'
FORMATS = (FORMAT_ONNX, FORMAT_TFLITE, FORMAT_TENSOR_RT, FORMAT_PT)

# Allowed image extensions
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')

# Dataset folders ratio
TRAINING_RATIO = 0.7
VALIDATION_RATIO = 0.2