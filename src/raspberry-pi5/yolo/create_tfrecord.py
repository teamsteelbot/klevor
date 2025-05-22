import argparse

import tensorflow as tf
import os

from args import get_attribute_from_args, parse_args_as_dict
from files import ensure_path_exists
from yolo import (YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS, ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_IMAGES,
    YOLO_DATASET_LABELS, ARGS_YOLO_VERSION, YOLO_DATASET_TESTING)
from yolo.args import add_yolo_input_model_argument, add_yolo_version_argument
from yolo.files import get_dataset_model_dir_path, get_tf_record_path


# This script creates a TFRecord file from images and their labels
def create_tfrecord(output_path, image_dir, label_dir):
    # Check if the output directory exists, if not create it
    ensure_path_exists(output_path)
    writer = tf.io.TFRecordWriter(output_path)

    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, os.path.splitext(image_name)[0] + ".txt")

        # Read image data
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

        # Read label data
        if os.path.exists(label_path):
            with open(label_path, "r") as label_file:
                label_data = label_file.read().strip()
        else:
            label_data = ""  # Default to empty if no label file exists

        # Create TFRecord features
        feature = {
            "image": tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_data])),
            "label": tf.train.Feature(bytes_list=tf.train.BytesList(value=[label_data.encode()])),
        }

        example = tf.train.Example(features=tf.train.Features(feature=feature))
        writer.write(example.SerializeToString())

    writer.close()

# Main function to run the script
def main() -> None:
    parser = argparse.ArgumentParser(description='Script to create TFRecord from images and labels')
    add_yolo_input_model_argument(parser)
    add_yolo_version_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = get_attribute_from_args(args, ARGS_YOLO_VERSION)

    # Get the dataset paths
    organized_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, YOLO_DATASET_TO_PROCESS,
                                                          arg_yolo_input_model)

    # Get the images and labels directories
    organized_to_process_testing_dir = os.path.join(organized_to_process_dir, YOLO_DATASET_TESTING)
    testing_images_dir = os.path.join(organized_to_process_testing_dir, YOLO_DATASET_IMAGES)
    testing_labels_dir = os.path.join(organized_to_process_testing_dir, YOLO_DATASET_LABELS)

    # Get the TF Record output path
    output_tfrecord = get_tf_record_path(arg_yolo_input_model, arg_yolo_version)

    # Create TFRecord
    create_tfrecord(output_tfrecord, testing_images_dir, testing_labels_dir)

if __name__ == "__main__":
    main()