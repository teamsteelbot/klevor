import os

# Folders (executed from root folder)
CWD = os.getcwd()

# ONNX metadata properties class names key
ONNX_METADATA_CLASS_NAMES_KEY = 'names'

# Spacer
SPACER = '_'

# YOLO model name
YOLO_NAME = 'steel_bot'

# Number of augmentations
YOLO_NUM_AUGMENTATIONS = 10

# Epochs
YOLO_EPOCHS = 100

# YOLO folders
YOLO_DIR = os.path.join(CWD, 'yolo')
YOLO_MODEL_2C = '2c'
YOLO_MODEL_4C = '4c'
YOLO_VERSION_5 = 'v5'
YOLO_VERSION_11 = 'v11'
YOLO_DATASET = os.path.join(YOLO, 'dataset')
YOLO_REPO = 'ultralytics/ultralytics'

# Yolo folders common suffixes and prefixes
YOLO_TO_PROCESS = 'to_process'
YOLO_PROCESSED = 'processed'

# YOLO dataset main folders
YOLO_DATASET_ORIGINAL = 'original'
YOLO_DATASET_RESIZED = 'resized'
YOLO_DATASET_LABELED = 'labeled'
YOLO_DATASET_AUGMENTED = 'augmented'
YOLO_DATASET_ORGANIZED = 'organized'

# YOLO models
BEST_ONNX = 'best.onnx'
BEST_PT = 'best.pt'
BEST_TENSOR_RT_QUANTIZED = 'best.engine'

# YOLO weights
YOLO_RUNS = 'runs'
YOLO_WEIGHTS = 'weights'

# YOLO zip folder
YOLO_ZIP = os.path.join(YOLO, 'zip')

# YOLO class colors
YOLO_2C_COLORS = {0: (68, 214, 44), 1: (238, 39, 55)}
YOLO_4C_COLORS = {0: (0, 51, 255), 1: (68, 214, 44), 2: (255, 102, 0), 3: (238, 39, 55)}

# Minimum confidence level and number of random images to test
YOLO_MINIMUM_CONFIDENCE_LEVEL = 0.70
YOLO_NUMBER_RANDOM_IMAGES = 10

# Arguments
ARGS_YOLO_FORMAT = 'format'
ARGS_YOLO_FORMAT_ONNX = 'onnx'
ARGS_YOLO_FORMAT_TFLITE = 'tflite'
ARGS_YOLO_FORMAT_TENSOR_RT = 'tensor_rt'
ARGS_YOLO_FORMAT_PT = 'pt'
ARGS_YOLO_QUANTIZED = 'quantized'
ARGS_YOLO_MODEL = 'model'
ARGS_YOLO_VERSION = 'version'