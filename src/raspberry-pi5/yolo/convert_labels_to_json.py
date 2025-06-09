from argparse import ArgumentParser
import json
import os

from yolo.args import Args
from yolo.files import Files


def convert_yolo_labels_to_json(annotations_dir, images_dir, output_json):
    """
    Convert YOLO labels to JSON format for Label Studio.
    """
    annotations = []

    for label_name in os.listdir(annotations_dir):
        image_name = label_name.replace(".txt", Files.DATASET_IMAGES_EXT)
        image_path = os.path.join(images_dir, image_name)

        with open(os.path.join(annotations_dir, label_name), "r") as f:
            objects = []
            for line in f:
                parts = line.strip().split()
                class_id, x_center, y_center, width, height = map(float, parts)
                objects.append({
                    "label": class_id,
                    "x": x_center,
                    "y": y_center,
                    "width": width,
                    "height": height
                })

        annotations.append({
            "image": image_path,
            "annotations": objects
        })

    with open(output_json, "w") as f:
        json.dump(annotations, f, indent=4)


def main() -> None:
    """
    Main function to run the script.
    """
    parser = ArgumentParser(description='Script to convert YOLO labels to JSON format for Label Studio')
    Args.add_yolo_input_model_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the dataset paths
    labeled_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_LABELED, Files.DATASET_TO_PROCESS,
                                                              arg_yolo_input_model)

    # Get the images and labels directories
    labeled_to_process_images_dir = os.path.join(labeled_to_process_dir, Files.DATASET_IMAGES)
    labeled_to_process_annotations_dir = os.path.join(labeled_to_process_dir, Files.DATASET_LABELS)

    # Get the output JSON file path
    labeled_annotations_json = os.path.join(labeled_to_process_dir, Files.DATASET_ANNOTATIONS_JSON)

    # Convert YOLO labels to JSON format
    convert_yolo_labels_to_json(labeled_to_process_annotations_dir, labeled_to_process_images_dir,
                                labeled_annotations_json)


if __name__ == "__main__":
    main()
