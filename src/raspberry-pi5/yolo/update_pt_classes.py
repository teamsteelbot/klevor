import argparse

import torch

from args import get_attribute_from_args, parse_args_as_dict
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION, ARGS_YOLO_CLASSES
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument, add_yolo_classes_argument
from yolo.files import get_model_best_pt_path

def update_classes(model_name, model_version, new_classes):
    """
    Update classes from a PyTorch model.
    """
    # Get the model path
    model_path = get_model_best_pt_path(model_name, model_version)

    # Load the model
    model = torch.load(model_path, weights_only=False)

    # Check if the model has the same number of classes as the new classes
    if len(model["model"].names) != len(new_classes):
        print(f"Error: The model has {len(model['model'].names)} classes, but the new classes have {len(new_classes)} classes.")
        return

    # Update class names
    model["model"].names = new_classes

    # Save the modified model
    torch.save(model, model_path)

def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to update YOLO model classes')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    add_yolo_classes_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the YOLO classes
    arg_yolo_classes = get_attribute_from_args(args, ARGS_YOLO_CLASSES)

    # Update the classes
    update_classes(arg_yolo_input_model, arg_yolo_version, arg_yolo_classes)

if __name__ == "__main__":
    main()