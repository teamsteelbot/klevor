from args.args import get_attribute_name
from yolo import (ARGS_YOLO_MODEL, YOLO_MODEL_2C, YOLO_MODEL_3C, YOLO_MODEL_4C, ARGS_YOLO_FORMAT_TFLITE,
                  ARGS_YOLO_FORMAT_TENSOR_RT,
                  ARGS_YOLO_FORMAT_ONNX, ARGS_YOLO_FORMAT, ARGS_YOLO_QUANTIZED, ARGS_YOLO_VERSION, YOLO_VERSION_5,
                  YOLO_VERSION_11,
                  ARGS_YOLO_FORMAT_PT, ARGS_YOLO_IS_RETRAINING)


# Add YOLO model argument to the parser
def add_yolo_model_argument(parser) -> None:
    parser.add_argument(get_attribute_name(ARGS_YOLO_MODEL), type=str, required=True, help='YOLO model',
                        choices=[YOLO_MODEL_2C, YOLO_MODEL_3C, YOLO_MODEL_4C])

# Add YOLO format argument to the parser
def add_yolo_format_argument(parser) -> None:
    parser.add_argument(get_attribute_name(ARGS_YOLO_FORMAT), type=str, required=True, help='YOLO format',
                        choices=[ARGS_YOLO_FORMAT_PT,ARGS_YOLO_FORMAT_TFLITE, ARGS_YOLO_FORMAT_TENSOR_RT, ARGS_YOLO_FORMAT_ONNX])

# Add YOLO quantized argument to the parser
def add_yolo_quantized_argument(parser) -> None:
    parser.add_argument(get_attribute_name(ARGS_YOLO_QUANTIZED), type=bool, required=False, help='YOLO model quantization', default=False)

# Add YOLO version argument to the parser
def add_yolo_version_argument(parser) -> None:
    parser.add_argument(get_attribute_name(ARGS_YOLO_VERSION), type=str, required=True, help='YOLO model version',
                        choices=[YOLO_VERSION_5, YOLO_VERSION_11])

# Add YOLO is retraining argument to the parser
def add_yolo_is_retraining_argument(parser) -> None:
    parser.add_argument(get_attribute_name(ARGS_YOLO_IS_RETRAINING), type=bool, required=False, help='YOLO model retraining', default=False)