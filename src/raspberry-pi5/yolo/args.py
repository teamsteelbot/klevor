from args import get_attribute_name
from yolo import (ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_FORMAT, ARGS_YOLO_QUANTIZED, ARGS_YOLO_VERSION, YOLO_VERSION_5,
                  YOLO_FORMAT_PT, ARGS_YOLO_RETRAINING, ARGS_YOLO_OUTPUT_MODEL, ARGS_YOLO_CLASSES,
                  ARGS_YOLO_IGNORE_CLASSES, ARGS_YOLO_EPOCHS, ARGS_YOLO_DEVICE, ARGS_YOLO_INPUT_MODEL_PT,
                  ARGS_YOLO_IMAGE_SIZE, YOLO_MODELS_NAME, YOLO_VERSIONS, YOLO_FORMATS)

def add_yolo_input_model_argument(parser) -> None:
    """
    Add YOLO input model argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_INPUT_MODEL), type=str, required=True, help='YOLO input model',
                        choices=YOLO_MODELS_NAME)

def add_yolo_input_model_pt_argument(parser) -> None:
    """
    Add YOLO input PyTorch model argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_INPUT_MODEL_PT), type=str, required=True, help='YOLO input PyTorch model')

def add_yolo_output_model_argument(parser) -> None:
    """
    Add YOLO output model argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_OUTPUT_MODEL), type=str, required=True, help='YOLO output model',
                        choices=YOLO_MODELS_NAME)

def add_yolo_format_argument(parser, required:bool=False) -> None:
    """
    Add YOLO format argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_FORMAT), type=str, required=required, help='YOLO format',
                        choices=YOLO_FORMATS, default=YOLO_FORMAT_PT)

def add_yolo_quantized_argument(parser, default:bool=False) -> None:
    """
    Add YOLO quantized argument to the parser.
    """
    parser.add_argument(f"--no-{ARGS_YOLO_QUANTIZED}", dest=ARGS_YOLO_QUANTIZED, action="store_false", help="Disable quantized")
    parser.add_argument(f"--{ARGS_YOLO_QUANTIZED}", dest=ARGS_YOLO_QUANTIZED, action="store_true", help="Enable quantized")
    parser.set_defaults(**{ARGS_YOLO_QUANTIZED: default})

def add_yolo_version_argument(parser) -> None:
    """
    Add YOLO version argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_VERSION), type=str, required=True, help='YOLO model version',
                        choices=YOLO_VERSIONS)

def add_yolo_retraining_argument(parser, default:bool=False) -> None:
    """
    Add YOLO retraining argument to the parser.
    """
    parser.add_argument(f"--no-{ARGS_YOLO_RETRAINING}", dest=ARGS_YOLO_RETRAINING, action="store_false",
                        help="Set retraining flag as 'False'")
    parser.add_argument(f"--{ARGS_YOLO_RETRAINING}", dest=ARGS_YOLO_RETRAINING, action="store_true",
                        help="Set retraining flag as 'True'")
    parser.set_defaults(**{ARGS_YOLO_RETRAINING: default})

def add_yolo_classes_argument(parser, required:bool=True) -> None:
    """
    Add YOLO classes argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_CLASSES), type=str, required=required, help='YOLO classes', nargs="*")

def add_yolo_ignore_classes_argument(parser, required:bool=True) -> None:
    """
    Add YOLO ignore classes argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_IGNORE_CLASSES), type=str, required=required, help='YOLO ignore classes', nargs="*")

def add_yolo_epochs_argument(parser, required:bool=True) -> None:
    """
    Add YOLO epochs argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_EPOCHS), type=int, required=required, help='YOLO epochs', default=100)

def add_yolo_device_argument(parser, required:bool=True) -> None:
    """
    Add YOLO device argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_DEVICE), type=str, required=required, help='YOLO device', default='0')

def add_yolo_image_size_argument(parser, required:bool=True) -> None:
    """
    Add YOLO image size argument to the parser.
    """
    parser.add_argument(get_attribute_name(ARGS_YOLO_IMAGE_SIZE), type=int, required=required, help='YOLO image size', default=640)