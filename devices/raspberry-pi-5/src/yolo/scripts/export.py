from argparse import ArgumentParser

from .. import Yolo
from ..args import Args
from ..constants import FORMAT_ONNX, FORMAT_TFLITE
from ..files import Files

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Script to export YOLO model to a given format'
    )
    args = Args(parser)
    args.add_yolo_input_model_argument()
    args.add_yolo_format_argument()
    args.add_yolo_quantized_argument()
    args.add_yolo_version_argument()

    # Get the YOLO input model
    arg_yolo_input_model = args.get_yolo_input_model()

    # Get the YOLO format
    arg_yolo_format = args.get_yolo_format()

    # Get the YOLO quantization
    arg_yolo_quantized = args.get_yolo_quantized()

    # Get the YOLO version
    arg_yolo_version = args.get_yolo_version()

    # Load a model
    model_path = Files.get_model_best_pt_path(
        arg_yolo_input_model,
        arg_yolo_version
    )
    model = Yolo.load(model_path)

    # Export the model
    path = None
    if arg_yolo_format == FORMAT_ONNX:
        path = Yolo.export_onnx(model)
    elif arg_yolo_quantized:
        if arg_yolo_format == FORMAT_TFLITE:
            path = Yolo.export_tflite(model, quantized=arg_yolo_quantized)

        else:
            path = Yolo.export_tensor_rt(model, quantized=arg_yolo_quantized)

    # Log
    print(f"Model exported to {path}")
