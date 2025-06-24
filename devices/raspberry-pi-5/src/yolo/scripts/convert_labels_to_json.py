import json
import os
from argparse import ArgumentParser

from ..args import Args, Flag
from ..files import Files
from ..files.constants import (
    DATASET_ANNOTATIONS_JSON,
    DATASET_IMAGES,
    DATASET_IMAGES_EXT,
    DATASET_LABELED,
    DATASET_LABELS,
    DATASET_TO_PROCESS,
)


def convert_yolo_labels_to_json(
    annotations_dir: str | os.PathLike[str],
    images_dir: str | os.PathLike[str],
    output_json: str | os.PathLike[str]
):
    """
    Convert YOLO labels to JSON format for Label Studio.

    Args:
        annotations_dir (str | os.PathLike[str]): Directory containing YOLO label files.
        images_dir (str | os.PathLike[str]): Directory containing the corresponding images.
        output_json (str | os.PathLike[str]): Path to save the output JSON file.
    """
    annotations = []

    for label_name in os.listdir(annotations_dir):
        image_name = label_name.replace(".txt", DATASET_IMAGES_EXT)
        image_path = os.path.join(images_dir, image_name)

        with open(os.path.join(annotations_dir, label_name), "r") as f:
            objects = []
            for line in f:
                parts = line.strip().split()
                class_id, x_center, y_center, width, height = map(float, parts)
                objects.append(
                    {
                        "label": class_id,
                        "x": x_center,
                        "y": y_center,
                        "width": width,
                        "height": height
                    }
                )

        annotations.append(
            {
                "image": image_path,
                "annotations": objects
            }
        )

    with open(output_json, "w") as f:
        json.dump(annotations, f, indent=4)


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Script to convert YOLO labels to JSON format for Label Studio'
    )
    Args.add_yolo_input_model_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args_dict(
        args,
        Flag.INPUT_MODEL
        )

    # Get the dataset paths
    labeled_to_process_dir = Files.get_dataset_model_dir_path(
        DATASET_LABELED,
        DATASET_TO_PROCESS,
        arg_yolo_input_model
        )

    # Get the images and labels directories
    labeled_to_process_images_dir = os.path.join(
        labeled_to_process_dir,
        DATASET_IMAGES
        )
    labeled_to_process_annotations_dir = os.path.join(
        labeled_to_process_dir,
        DATASET_LABELS
        )

    # Get the output JSON file path
    labeled_annotations_json = os.path.join(
        labeled_to_process_dir,
        DATASET_ANNOTATIONS_JSON
        )

    # Convert YOLO labels to JSON format
    convert_yolo_labels_to_json(
        labeled_to_process_annotations_dir,
        labeled_to_process_images_dir,
        labeled_annotations_json
        )
