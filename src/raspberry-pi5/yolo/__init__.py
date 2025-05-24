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
YOLO_G_COLORS = {0: GREEN_COLOR}
YOLO_M_COLORS = {0: MAGENTA_COLOR}
YOLO_R_COLORS = {0: RED_COLOR}
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
YOLO_MODEL_G = 'g'
YOLO_MODEL_R = 'r'
YOLO_MODEL_GR = 'gr'
YOLO_MODEL_GMR = 'gmr'
YOLO_MODEL_BGOR = 'bgor'
YOLO_MODELS_NAME = [YOLO_MODEL_M, YOLO_MODEL_G, YOLO_MODEL_R, YOLO_MODEL_GR, YOLO_MODEL_GMR, YOLO_MODEL_BGOR]

# YOLO model versions
YOLO_VERSION_5 = 'v5'
YOLO_VERSION_11 = 'v11'
YOLO_VERSIONS = [YOLO_VERSION_5, YOLO_VERSION_11]

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
YOLO_DATASET_IMAGES = 'images'
YOLO_DATASET_LABELS = 'labels'
YOLO_DATASET_TRAINING = 'train'
YOLO_DATASET_VALIDATIONS = 'val'
YOLO_DATASET_TESTING = 'test'
YOLO_DATASET_ANNOTATIONS_JSON = 'annotations.json'
YOLO_DATASET_CLASSES_TXT = 'classes.txt'
YOLO_DATASET_NOTES_JSON = 'notes.json'
YOLO_DATASET_IMAGES_EXT = '.jpg'

# YOLO dataset status folders
YOLO_DATASET_TO_PROCESS = 'to_process'
YOLO_DATASET_PROCESSED = 'processed'
YOLO_DATASET_STATUSES = [YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED]

# YOLO Hailo-related folders
YOLO_HAILO = 'hailo'
YOLO_HAILO_LABELS = 'labels'
YOLO_HAILO_CALIB = 'calib'
YOLO_HAILO_SUITE = 'suite'
YOLO_HAILO_LIBS = 'libs'
YOLO_HAILO_MODEL_ZOO = 'hailo_model_zoo'

# YOLO models
BEST = 'best'
BEST_ONNX = 'best.onnx'
BEST_PT = 'best.pt'
BEST_TENSOR_RT_QUANTIZED = 'best.engine'
LAST = 'last'

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

# YOLO formats
YOLO_FORMAT_ONNX = 'onnx'
YOLO_FORMAT_TFLITE = 'tflite'
YOLO_FORMAT_TENSOR_RT = 'tensor_rt'
YOLO_FORMAT_PT = 'pt'
YOLO_FORMATS = [YOLO_FORMAT_ONNX, YOLO_FORMAT_TFLITE, YOLO_FORMAT_TENSOR_RT, YOLO_FORMAT_PT]

# Arguments
ARGS_DEBUG = 'debug'
ARGS_YOLO_FORMAT = 'format'
ARGS_YOLO_QUANTIZED = 'quantized'
ARGS_YOLO_INPUT_MODEL = 'input-model'
ARGS_YOLO_INPUT_MODEL_PT = 'input-model-pt'
ARGS_YOLO_OUTPUT_MODEL = 'output-model'
ARGS_YOLO_VERSION = 'version'
ARGS_YOLO_RETRAINING = 'retraining'
ARGS_YOLO_CLASSES = 'classes'
ARGS_YOLO_IGNORE_CLASSES = 'ignore-classes'
ARGS_YOLO_EPOCHS = 'epochs'
ARGS_YOLO_DEVICE = 'device'
ARGS_YOLO_IMAGE_SIZE = 'imgsz'

# Ignore lists
ZIP_IGNORE_DIR = ['.git', '.venv', '.idea', 'raspberry-pi-pico2', 'scripts', 'yolo']

# Logs folders
LOG_DIR = os.path.join(CWD, 'logs')
LOGS_DIR = os.path.join(LOG_DIR, 'logs')

def add_single_quotes_to_list_elements(lst: list) -> list:
    """
    Add single quotes to each element from the list.
    """
    return [f"'{item}'" for item in lst]

def check_model_name(model_name: str) -> None:
    """
    Check the validity of model name.
    """
    if model_name not in YOLO_MODELS_NAME:
        mapped_yolo_models_name = add_single_quotes_to_list_elements(YOLO_MODELS_NAME)
        raise ValueError(f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.")

def check_yolo_version(yolo_version: str) -> None:
    """
    Check the validity of YOLO version.
    """
    if yolo_version not in YOLO_VERSIONS:
        mapped_yolo_versions = add_single_quotes_to_list_elements(YOLO_MODELS_NAME)
        raise ValueError(f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.")

def check_dataset_status(dataset_status: str|None) -> None:
    """
    Check the validity of dataset status.
    """
    if dataset_status is not None:
        if dataset_status not in [YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED]:
            mapped_yolo_dataset_statuses = add_single_quotes_to_list_elements(YOLO_DATASET_STATUSES)
            raise ValueError(f"Invalid dataset status: {dataset_status}. Must be one of the following: {', '.join(mapped_yolo_dataset_statuses)}.")

def check_model_dataset_status(dataset_name: str, dataset_status: str|None) -> None:
    """
    Check the validity of model dataset status.
    """
    # Check if the dataset name is split by dataset status
    if dataset_status is not None:
        if dataset_name in [YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with dataset status '{dataset_status}'.")

def check_dataset_name(dataset_name: str) -> None:
    """
    Check the validity of dataset name.
    """
    # Check the validity of dataset name
    if dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED, YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED,
                            YOLO_DATASET_ORGANIZED]:
        raise ValueError(f"Invalid dataset name: {dataset_name}. Must be one of the defined dataset folders.")

def check_model_dataset_name(dataset_name:str, model_name:str|None)-> None:
    """
    Check the validity of the model dataset name.
    """
    # Check if the dataset name is split by model name
    if model_name is not None:
        if dataset_name in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
            raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used with model name '{model_name}'.")

    # Check if the dataset name is split by model name
    elif dataset_name not in [YOLO_DATASET_ORIGINAL, YOLO_DATASET_RESIZED]:
        raise ValueError(f"Invalid dataset path. The dataset name '{dataset_name}' should not be used without a model name.")


def get_model_classes_color_pallete(model_name: str) -> dict[int, tuple[int, int, int]] | None:
    """
    Get the model classes color palette.
    """
    # Check the validity of the model name
    check_model_name(model_name)

    if model_name == YOLO_MODEL_G:
        return YOLO_G_COLORS
    if model_name == YOLO_MODEL_M:
        return YOLO_M_COLORS
    if model_name == YOLO_MODEL_R:
        return YOLO_R_COLORS
    if model_name == YOLO_MODEL_GR:
        return YOLO_GR_COLORS
    if model_name == YOLO_MODEL_GMR:
        return YOLO_GMR_COLORS
    if model_name == YOLO_MODEL_BGOR:
        return YOLO_BGOR_COLORS