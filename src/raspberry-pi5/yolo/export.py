import argparse

from yolo import Yolo
from yolo.args import Args
from yolo.files import Files


def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to export YOLO model to a given format')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_format_argument(parser)
    Args.add_yolo_quantized_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO format
    arg_yolo_format = Args.get_attribute_from_args(args, Args.FORMAT)

    # Get the YOLO quantization
    arg_yolo_quantized = Args.get_attribute_from_args(args, Args.QUANTIZED)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Load a model
    model_path = Files.get_model_best_pt_path(arg_yolo_input_model, arg_yolo_version)
    model = Yolo.load(model_path)

    # Export the model
    path = None
    if arg_yolo_format == Yolo.FORMAT_ONNX:
        path = Yolo.export_onnx(model)
    elif arg_yolo_quantized:
        if arg_yolo_format == Yolo.FORMAT_TFLITE:
            path = Yolo.export_tflite(model, quantized=arg_yolo_quantized)

        else:
            path = Yolo.export_tensor_rt(model, quantized=arg_yolo_quantized)

    # Log
    print(f"Model exported to {path}")


if __name__ == '__main__':
    main()
