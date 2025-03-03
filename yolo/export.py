import argparse
from model.model_yolo import load, export_onnx, export_tflite
from yolo.constants import ARGS_YOLO_FORMAT, ARGS_YOLO_QUANTIZED, ARGS_YOLO_FORMAT_ONNX, ARGS_YOLO_MODEL, \
    ARGS_YOLO_MODEL_4C, ARGS_YOLO_MODEL_2C, YOLO_RUNS_2C_WEIGHTS_BEST_PT, YOLO_RUNS_4C_WEIGHTS_BEST_PT, \
    ARGS_YOLO_FORMAT_TFLITE, ARGS_YOLO_FORMAT_TENSOR_RT, ARGS_YOLO_MODEL_PROP, ARGS_YOLO_FORMAT_PROP, \
    ARGS_YOLO_QUANTIZED_PROP

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to export YOLO model to a given format')
    parser.add_argument(ARGS_YOLO_MODEL, type=str, required=True, help='YOLO model', choices=[ARGS_YOLO_MODEL_2C, ARGS_YOLO_MODEL_4C])
    parser.add_argument(ARGS_YOLO_FORMAT, type=str, required=True, help='YOLO format', choices=[ARGS_YOLO_FORMAT_TFLITE, ARGS_YOLO_FORMAT_TENSOR_RT, ARGS_YOLO_FORMAT_ONNX])
    parser.add_argument(ARGS_YOLO_QUANTIZED, type=bool, required=False, help='YOLO model quantization')
    args = parser.parse_args()

    # Get the YOLO model
    arg_yolo_model = getattr(args, ARGS_YOLO_MODEL_PROP)

    # Get the YOLO format
    arg_yolo_format = getattr(args, ARGS_YOLO_FORMAT_PROP)

    # Get the YOLO quantization
    arg_yolo_quantized = getattr(args, ARGS_YOLO_QUANTIZED_PROP)
    if arg_yolo_quantized is None:
        arg_yolo_quantized = False

    # Load a model
    model_path = None
    if arg_yolo_model == ARGS_YOLO_MODEL_2C:
        model_path = YOLO_RUNS_2C_WEIGHTS_BEST_PT

    elif arg_yolo_model == ARGS_YOLO_MODEL_4C:
        model_path = YOLO_RUNS_4C_WEIGHTS_BEST_PT
    model = load(model_path)

    # Export the model
    path=None
    if arg_yolo_format == ARGS_YOLO_FORMAT_ONNX:
        path = export_onnx(model)

    elif arg_yolo_format == ARGS_YOLO_FORMAT_TFLITE:
        path = export_tflite(model, quantized=arg_yolo_quantized)

    else:
        path = export_tflite(model, quantized=arg_yolo_quantized)

    # Log
    print(f"Model exported to {path}")