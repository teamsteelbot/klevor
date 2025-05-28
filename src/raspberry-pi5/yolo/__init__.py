from model import Yolo as Y
from utils import add_single_quotes_to_list_elements


class Yolo(Y):
    """
    YOLO constants and utility functions class.

    This class contains constants related to YOLO models, directories, colors, and utility functions
    for checking model names, versions, dataset statuses, and dataset names.
    """
    # ONNX metadata properties class names key
    ONNX_METADATA_CLASS_NAMES_KEY = 'names'

    # Number of augmentations
    NUM_AUGMENTATIONS = 10

    # Colors
    GREEN_COLOR = (68, 214, 44)
    MAGENTA_COLOR = (255, 0, 255)
    RED_COLOR = (238, 39, 55)
    BLUE_COLOR = (0, 51, 255)
    ORANGE_COLOR = (255, 102, 0)

    # Epochs
    EPOCHS = 100

    # Image size
    IMAGE_SIZE = 640

    # YOLO model names
    MODEL_M = 'm'
    MODEL_G = 'g'
    MODEL_R = 'r'
    MODEL_GR = 'gr'
    MODEL_GMR = 'gmr'
    MODEL_BGOR = 'bgor'
    MODELS_NAME = (MODEL_M, MODEL_G, MODEL_R, MODEL_GR, MODEL_GMR, MODEL_BGOR)

    # YOLO class colors
    MODEL_G_COLORS = {0: GREEN_COLOR}
    MODEL_M_COLORS = {0: MAGENTA_COLOR}
    MODEL_R_COLORS = {0: RED_COLOR}
    MODEL_GR_COLORS = {0: GREEN_COLOR, 1: RED_COLOR}
    MODEL_GMR_COLORS = {0: GREEN_COLOR, 1: MAGENTA_COLOR, 2: RED_COLOR}
    MODEL_BGOR_COLORS = {0: BLUE_COLOR, 1: GREEN_COLOR, 2: ORANGE_COLOR, 3: RED_COLOR}

    # YOLO model versions
    VERSION_5 = 'v5'
    VERSION_11 = 'v11'
    VERSIONS = (VERSION_5, VERSION_11)

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

    @classmethod
    def check_model_name(cls, model_name: str) -> None:
        """
        Check the validity of model name.
        """
        if model_name not in cls.MODELS_NAME:
            mapped_yolo_models_name = add_single_quotes_to_list_elements(cls.MODELS_NAME)
            raise ValueError(
                f"Invalid model name: {model_name}. Must be one of the following: {', '.join(mapped_yolo_models_name)}.")

    @classmethod
    def check_yolo_version(cls, yolo_version: str) -> None:
        """
        Check the validity of YOLO version.
        """
        if yolo_version not in cls.VERSIONS:
            mapped_yolo_versions = add_single_quotes_to_list_elements(cls.MODELS_NAME)
            raise ValueError(
                f"Invalid yolo version: {yolo_version}. Must be one of the following: {', '.join(mapped_yolo_versions)}.")

    @classmethod
    def get_model_classes_color_palette(cls, model_name: str) -> dict[int, tuple[int, int, int]] | None:
        """
        Get the model classes color palette.
        """
        # Check the validity of the model name
        cls.check_model_name(model_name)

        if model_name == cls.MODEL_G:
            return cls.MODEL_G_COLORS

        if model_name == cls.MODEL_M:
            return cls.MODEL_M_COLORS

        if model_name == cls.MODEL_R:
            return cls.MODEL_R_COLORS

        if model_name == cls.MODEL_GR:
            return cls.MODEL_GR_COLORS

        if model_name == cls.MODEL_GMR:
            return cls.MODEL_GMR_COLORS

        if model_name == cls.MODEL_BGOR:
            return cls.MODEL_BGOR_COLORS
