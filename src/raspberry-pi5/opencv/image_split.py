import random
import os
from typing import LiteralString

from files import copy_file, move_folder
from yolo import (YOLO_DATASET_IMAGES, YOLO_DATASET_LABELS, YOLO_DATASET_TRAINING, YOLO_DATASET_VALIDATIONS,
                  YOLO_DATASET_TESTING)


# Split the dataset into processed, validation, and testing sets
def split_dataset(input_dir: LiteralString, output_dir: LiteralString,
                  train_ratio=0.7,
                  val_ratio=0.2):
    input_images_dir = os.path.join(input_dir, YOLO_DATASET_IMAGES)
    input_annotations_dir = os.path.join(input_dir, YOLO_DATASET_LABELS)
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
        if io_dir is not None and not os.path.exists(io_dir):
            os.makedirs(io_dir)

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
    os.rmdir(input_images_dir)
    os.rmdir(input_annotations_dir)
