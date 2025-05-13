import argparse

from model.yolo import load, export_onnx, export_tflite, export_tensor_rt
from yolo import (ARGS_YOLO_FORMAT_ONNX, ARGS_YOLO_FORMAT_TFLITE, ARGS_YOLO_MODEL, ARGS_YOLO_FORMAT,
                  ARGS_YOLO_QUANTIZED, ARGS_YOLO_VERSION)
from yolo.args import (add_yolo_model_argument, add_yolo_format_argument, add_yolo_quantized_argument,
    add_yolo_version_argument)
from yolo.files import get_model_best_pt_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to export YOLO model to a given format')
    add_yolo_model_argument(parser)
    add_yolo_format_argument(parser)
    add_yolo_quantized_argument(parser)
    add_yolo_version_argument(parser)
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL)

    # Get the YOLO format
    arg_yolo_format = getattr(args, ARGS_YOLO_FORMAT)

    # Get the YOLO quantization
    arg_yolo_quantized = getattr(args, ARGS_YOLO_QUANTIZED)

    # Get the YOLO version
    arg_yolo_version = getattr(args, ARGS_YOLO_VERSION)

    # Load a model
    model_path = get_model_best_pt_path(arg_yolo_model, arg_yolo_version)
    model = load(model_path)

    # Export the model
    path = None
    if arg_yolo_format == ARGS_YOLO_FORMAT_ONNX:
        path = export_onnx(model)

    elif arg_yolo_format == ARGS_YOLO_FORMAT_TFLITE:
        path = export_tflite(model, quantized=arg_yolo_quantized)

    else:
        path = export_tensor_rt(model, quantized=arg_yolo_quantized)

    # Log
    print(f"Model exported to {path}")
