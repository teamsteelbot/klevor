import argparse
import random
import os
import shutil
from typing import LiteralString

from args import get_attribute_from_args, parse_args_as_dict
from files import copy_file, ensure_path_exists
from yolo import (ARGS_YOLO_INPUT_MODEL, YOLO_DATASET_AUGMENTED, YOLO_DATASET_ORGANIZED,
                  YOLO_DATASET_IMAGES, YOLO_DATASET_LABELS, YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS,
                  YOLO_DATASET_TESTING)
from yolo.args import add_yolo_input_model_argument
from yolo.files import get_dataset_model_dir_path


def split_dataset(input_dir: LiteralString, output_dir: LiteralString,
                  train_ratio=0.7,
                  val_ratio=0.2):
    """
    Split the dataset into processed, validation, and testing sets.
    """
    # Get the input images and annotations directories
    input_images_dir = os.path.join(input_dir, YOLO_DATASET_IMAGES)
    input_annotations_dir = os.path.join(input_dir, YOLO_DATASET_LABELS)

    # Get the output directories
    output_training_dir = os.path.join(output_dir, YOLO_DATASET_TRAINING)
    output_validations_dir = os.path.join(output_dir, YOLO_DATASET_VALIDATIONS)
    output_testing_dir = os.path.join(output_dir, YOLO_DATASET_TESTING)
    output_training_images_dir = os.path.join(output_training_dir, YOLO_DATASET_IMAGES)
    output_validations_images_dir = os.path.join(output_validations_dir, YOLO_DATASET_IMAGES)
    output_testing_images_dir = os.path.join(output_testing_dir, YOLO_DATASET_IMAGES)
    output_training_annotations_dir = os.path.join(output_training_dir, YOLO_DATASET_LABELS)
    output_validations_annotations_dir = os.path.join(output_validations_dir, YOLO_DATASET_LABELS)
    output_testing_annotations_dir = os.path.join(output_testing_dir, YOLO_DATASET_LABELS)

    # Check if the path exists, if not it creates it
    for io_dir in [input_dir, input_images_dir, input_annotations_dir, output_dir, output_training_dir,
                   output_validations_dir, output_testing_dir, output_training_images_dir,
                   output_validations_images_dir, output_testing_images_dir,
                   output_training_annotations_dir, output_validations_annotations_dir,
                   output_testing_annotations_dir]:
        ensure_path_exists(io_dir)

    # Get the list of files
    image_filenames = os.listdir(input_images_dir)
    if len(image_filenames) == 0:
        print(f"Warning: No images found in {input_images_dir}")
        return

    random.shuffle(image_filenames)

    # Split the processed
    train_split = int(len(image_filenames) * train_ratio)
    val_split = int(len(image_filenames) * val_ratio)

    # Copy the files to the output directories
    for i, image_filename in enumerate(image_filenames):
        # Get the image and annotations paths
        input_to_process_image_path = os.path.join(input_images_dir, image_filename)
        annotations_filename = os.path.splitext(image_filename)[0] + '.txt'
        input_to_process_annotations_path = os.path.join(input_annotations_dir, annotations_filename)

        if i < train_split:
            copy_file(input_to_process_image_path, output_training_images_dir)
            copy_file(input_to_process_annotations_path, output_training_annotations_dir)
        elif i < train_split + val_split:
            copy_file(input_to_process_image_path, output_validations_images_dir)
            copy_file(input_to_process_annotations_path, output_validations_annotations_dir)
        else:
            copy_file(input_to_process_image_path, output_testing_images_dir)
            copy_file(input_to_process_annotations_path, output_testing_annotations_dir)

        # Log
        print(f'Copied {image_filename} to the respective directories')

    # Remove the images and annotations folders
    shutil.rmtree(input_images_dir)
    shutil.rmtree(input_annotations_dir)

def main() -> None:
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to split YOLO dataset images and labels')
    add_yolo_input_model_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the dataset paths
    augmented_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, None, arg_yolo_input_model)
    organized_dir = get_dataset_model_dir_path(YOLO_DATASET_ORGANIZED, None, arg_yolo_input_model)

    # Split the images
    split_dataset(augmented_dir, organized_dir)

if __name__ == '__main__':
    main()