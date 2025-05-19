import os

# Folders (executed from root folder)
CWD = os.getcwd()

# ONNX metadata properties class names key
ONNX_METADATA_CLASS_NAMES_KEY = 'names'

# Number of augmentations
YOLO_NUM_AUGMENTATIONS = 10

# Colors
GREEN_COLOR = (68, 214, 44)
MAGENTA_COLOR = (255, 0, 255)
RED_COLOR = (238, 39, 55)
BLUE_COLOR = (0, 51, 255)
ORANGE_COLOR = (255, 102, 0)

# YOLO class colors
YOLO_M_COLORS = {0: MAGENTA_COLOR}
YOLO_GR_COLORS = {0: GREEN_COLOR, 1: RED_COLOR}
YOLO_GMR_COLORS = {0: GREEN_COLOR, 1: MAGENTA_COLOR, 2: RED_COLOR}
YOLO_BGOR_COLORS = {0: BLUE_COLOR, 1: GREEN_COLOR, 2: ORANGE_COLOR, 3: RED_COLOR}

# Epochs
YOLO_EPOCHS = 100

# Image size
YOLO_IMAGE_SIZE = 640

# YOLO folder
YOLO_DIR = os.path.join(CWD, 'yolo')

# YOLO model names
YOLO_MODEL_M = 'm'
YOLO_MODEL_GR = 'gr'
YOLO_MODEL_GMR = 'gmr'
YOLO_MODEL_BGOR = 'bgor'

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
YOLO_DATASET_ANNOTATIONS_JSON = 'annotations.json'
YOLO_DATASET_CLASSES_TXT = 'classes.txt'
YOLO_DATASET_NOTES_JSON = 'notes.json'
YOLO_DATASET_IMAGES_EXT = '.jpg'

# YOLO Hailo-related folders
YOLO_HAILO = 'hailo'
YOLO_SUITE = 'suite'
YOLO_LIBS = 'libs'
YOLO_HAILO_MODEL_ZOO = 'hailo_model_zoo'

# YOLO models
BEST_ONNX = 'best.onnx'
BEST_PT = 'best.pt'
BEST_TENSOR_RT_QUANTIZED = 'best.engine'

# TF Records
YOLO_TF_RECORDS = 'tf_records'

# YOLO runs
YOLO_RUNS_OLD = 'runs_old'
YOLO_RUNS = 'runs'

# YOLO weights
YOLO_WEIGHTS = 'weights'

# YOLO zip folder
YOLO_ZIP = 'zip'

# Minimum confidence level and number of random images to test
YOLO_MINIMUM_CONFIDENCE_LEVEL = 0.70
YOLO_NUMBER_RANDOM_IMAGES = 10

# Arguments
ARGS_YOLO_FORMAT = 'format'
ARGS_YOLO_QUANTIZED = 'quantized'
ARGS_YOLO_INPUT_MODEL = 'input-model'
ARGS_YOLO_INPUT_MODEL_PT = 'input-model-pt'
ARGS_YOLO_OUTPUT_MODEL = 'output-model'
ARGS_YOLO_VERSION = 'version'
ARGS_YOLO_IS_RETRAINING = 'is-retraining'
ARGS_YOLO_CLASSES = 'classes'
ARGS_YOLO_IGNORE_CLASSES = 'ignore-classes'
ARGS_YOLO_EPOCHS = 'epochs'
ARGS_YOLO_DEVICE = 'device'
ARGS_YOLO_IMAGE_SIZE = 'imgsz'

# YOLO formats
ARGS_YOLO_FORMAT_ONNX = 'onnx'
ARGS_YOLO_FORMAT_TFLITE = 'tflite'
ARGS_YOLO_FORMAT_TENSOR_RT = 'tensor_rt'
ARGS_YOLO_FORMAT_PT = 'pt'

# Ignore lists
ZIP_IGNORE_DIR = ['.git', '.venv', '.idea', 'raspberry-pi-pico2', 'scripts', 'yolo']