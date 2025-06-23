from argparse import ArgumentParser
import os

import tensorflow as tf

from ..args import Args, Flag
from ..files import Files
from ..files.constants import DATASET_ORGANIZED, DATASET_TO_PROCESS, DATASET_TESTING, DATASET_IMAGES, DATASET_LABELS


def create_tfrecord(output_path: str | os.PathLike[str], image_dir: str | os.PathLike[str],
                    label_dir: str | os.PathLike[str]):
    """
    This script creates a TFRecord file from images and their labels.

    Args:
        output_path (str | os.PathLike[str]): The path where the TFRecord file will be saved.
        image_dir (str | os.PathLike[str]): The directory containing the images.
        label_dir (str | os.PathLike[str]): The directory containing the label files.
    """
    # Check if the output directory exists, if not create it
    Files.ensure_directory_exists(output_path)
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


if __name__ == "__main__":
    parser = ArgumentParser(description='Script to create TFRecord from images and labels')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args_dict(args, Flag.INPUT_MODEL)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args_dict(args, Flag.VERSION)

    # Get the dataset paths
    organized_to_process_dir = Files.get_dataset_model_dir_path(DATASET_ORGANIZED, DATASET_TO_PROCESS,
                                                               arg_yolo_input_model)

    # Get the images and labels directories
    organized_to_process_testing_dir = os.path.join(organized_to_process_dir, DATASET_TESTING)
    testing_images_dir = os.path.join(organized_to_process_testing_dir, DATASET_IMAGES)
    testing_labels_dir = os.path.join(organized_to_process_testing_dir, DATASET_LABELS)

    # Get the TF Record output path
    output_tfrecord = Files.get_tf_record_path(arg_yolo_input_model, arg_yolo_version)

    # Create TFRecord
    create_tfrecord(output_tfrecord, testing_images_dir, testing_labels_dir)
