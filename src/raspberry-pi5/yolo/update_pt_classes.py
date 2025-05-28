import argparse

import torch

from yolo.args import Args
from yolo.files import Files


def update_classes(model_name: str, model_version: str, new_classes: list[str]):
    """
    Update classes from a PyTorch model.

    Args:
        model_name (str): Name of the YOLO model.
        model_version (str): Version of the YOLO model.
        new_classes (list): List of new class names to update in the model.

    Returns:
        None
    """
    # Get the model path
    model_path = Files.get_model_best_pt_path(model_name, model_version)

    # Load the model
    model = torch.load(model_path, weights_only=False)

    # Check if the model has the same number of classes as the new classes
    if len(model["model"].names) != len(new_classes):
        print(
            f"Error: The model has {len(model['model'].names)} classes, but the new classes have {len(new_classes)} classes.")
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
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    Args.add_yolo_classes_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the YOLO classes
    arg_yolo_classes = Args.get_attribute_from_args(args, Args.CLASSES)

    # Update the classes
    update_classes(arg_yolo_input_model, arg_yolo_version, arg_yolo_classes)


if __name__ == "__main__":
    main()
