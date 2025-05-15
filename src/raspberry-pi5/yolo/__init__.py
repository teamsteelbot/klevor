import os

# Folders (executed from root folder)
CWD = os.getcwd()

# ONNX metadata properties class names key
ONNX_METADATA_CLASS_NAMES_KEY = 'names'

# Number of augmentations
YOLO_NUM_AUGMENTATIONS = 10

# Epochs
YOLO_EPOCHS = 100

# Image size
YOLO_IMAGE_SIZE = 640

# YOLO folder
YOLO_DIR = os.path.join(CWD, 'yolo')

# YOLO model names
YOLO_MODEL_2C = '2c'
YOLO_MODEL_3C = '3c'
YOLO_MODEL_4C = '4c'

# YOLO model versions
YOLO_VERSION_5 = 'v5'
YOLO_VERSION_11 = 'v11'

# YOLO data
YOLO_DATA = 'data'

# YOLO colab
YOLO_COLAB = 'colab'

# YOLO local
YOLO_LOCAL = 'local'

# YOLO notebooks
YOLO_NOTEBOOKS = 'notebooks'

# YOLO dataset folders
YOLO_DATASET = os.path.join(YOLO_DIR, 'dataset')
YOLO_DATASET_GENERAL = 'general'
YOLO_DATASET_ORIGINAL = 'original'
YOLO_DATASET_RESIZED = 'resized'
YOLO_DATASET_LABELED = 'labeled'
YOLO_DATASET_AUGMENTED = 'augmented'
YOLO_DATASET_ORGANIZED = 'organized'
YOLO_DATASET_TO_PROCESS = 'to_process'
YOLO_DATASET_PROCESSED = 'processed'
YOLO_DATASET_IMAGES = 'images'
YOLO_DATASET_LABELS = 'labels'
YOLO_DATASET_TRAINING = 'train'
YOLO_DATASET_VALIDATIONS = 'val'
YOLO_DATASET_TESTING = 'test'

# YOLO models
BEST_ONNX = 'best.onnx'
BEST_PT = 'best.pt'
BEST_TENSOR_RT_QUANTIZED = 'best.engine'

# YOLO runs
YOLO_RUNS_OLD = 'runs_old'
YOLO_RUNS = 'runs'

# YOLO weights
YOLO_WEIGHTS = 'weights'

# YOLO zip folder
YOLO_ZIP = 'zip'

# YOLO class colors
YOLO_2C_COLORS = {0: (68, 214, 44), 1: (238, 39, 55)}
YOLO_3C_COLORS = {0: (68, 214, 44), 1: (238, 39, 55), 2: (255, 0, 255)}
YOLO_4C_COLORS = {0: (0, 51, 255), 1: (68, 214, 44), 2: (255, 102, 0), 3: (238, 39, 55)}

# Minimum confidence level and number of random images to test
YOLO_MINIMUM_CONFIDENCE_LEVEL = 0.70
YOLO_NUMBER_RANDOM_IMAGES = 10

# Arguments
ARGS_YOLO_FORMAT = 'format'
ARGS_YOLO_QUANTIZED = 'quantized'
ARGS_YOLO_MODEL = 'model'
ARGS_YOLO_VERSION = 'version'
ARGS_YOLO_IS_RETRAINING = 'is-retraining'

# YOLO formats
ARGS_YOLO_FORMAT_ONNX = 'onnx'
ARGS_YOLO_FORMAT_TFLITE = 'tflite'
ARGS_YOLO_FORMAT_TENSOR_RT = 'tensor_rt'
ARGS_YOLO_FORMAT_PT = 'pt'

# Ignore lists
ZIP_IGNORE_DIR = ['.git', '.venv', '.idea', 'raspberry-pi-pico2', 'scripts', 'yolo']