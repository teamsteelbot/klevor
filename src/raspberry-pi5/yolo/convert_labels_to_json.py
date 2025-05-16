import argparse
import os
import json

from args.args import get_attribute_from_args, parse_args_as_dict
from yolo import ARGS_YOLO_INPUT_MODEL, ARGS_YOLO_VERSION, YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_IMAGES, \
    YOLO_DATASET_LABELS, YOLO_DATASET_IMAGES_EXT, YOLO_DATASET_ANNOTATIONS_JSON
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import get_dataset_model_dir_path

# Convert YOLO labels to JSON format for Label Studio
def convert_yolo_labels_to_json(annotations_dir, images_dir, output_json):
    annotations = []

    for label_name in os.listdir(annotations_dir):
        image_name = label_name.replace(".txt", YOLO_DATASET_IMAGES_EXT)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to convert YOLO labels to JSON format for Label Studio')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the dataset paths
    labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS,
                                                        arg_yolo_input_model)

    # Get the images and labels directories
    labeled_to_process_images_dir = os.path.join(labeled_to_process_dir, YOLO_DATASET_IMAGES)
    labeled_to_process_annotations_dir = os.path.join(labeled_to_process_dir, YOLO_DATASET_LABELS)

    # Get the output JSON file path
    labeled_annotations_json = os.path.join(labeled_to_process_dir, YOLO_DATASET_ANNOTATIONS_JSON)

    # Convert YOLO labels to JSON format
    convert_yolo_labels_to_json(labeled_to_process_annotations_dir, labeled_to_process_images_dir, labeled_annotations_json)