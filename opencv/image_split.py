import random
import os
from files.files import copy_file, move_folder
from opencv.constants import IMAGES, LABELS, TRAINING, VALIDATIONS, TESTING

# Split the images into processed, validation, and testing sets
def split_images(input_to_process_dir: str, output_organized_to_process_dir: str, output_processed_dir: str = None, train_ratio=0.7,
               val_ratio=0.2):
    input_to_process_images_dir = os.path.join(input_to_process_dir, IMAGES)
    input_to_process_annotations_dir = os.path.join(input_to_process_dir, LABELS)
    output_processed_images_dir = os.path.join(output_processed_dir, IMAGES)
    output_processed_annotations_dir = os.path.join(output_processed_dir, LABELS)
    output_organized_training_dir = os.path.join(output_organized_to_process_dir, TRAINING)
    output_organized_validations_dir = os.path.join(output_organized_to_process_dir, VALIDATIONS)
    output_organized_testing_dir = os.path.join(output_organized_to_process_dir, TESTING)
    output_organized_training_images_dir = os.path.join(output_organized_training_dir, IMAGES)
    output_organized_validations_images_dir = os.path.join(output_organized_validations_dir, IMAGES)
    output_organized_testing_images_dir = os.path.join(output_organized_testing_dir, IMAGES)
    output_organized_training_annotations_dir = os.path.join(output_organized_training_dir, LABELS)
    output_organized_validations_annotations_dir = os.path.join(output_organized_validations_dir, LABELS)
    output_organized_testing_annotations_dir = os.path.join(output_organized_testing_dir, LABELS)

    # Check if the path exists, if not it creates it
    for io_dir in [input_to_process_dir, input_to_process_images_dir, input_to_process_annotations_dir,
                   output_processed_dir, output_processed_images_dir, output_processed_annotations_dir,
                   output_organized_to_process_dir, output_organized_training_dir, output_organized_validations_dir,
                   output_organized_testing_dir, output_organized_training_images_dir,
                   output_organized_validations_images_dir, output_organized_testing_images_dir,
                   output_organized_training_annotations_dir, output_organized_validations_annotations_dir,
                   output_organized_testing_annotations_dir]:
        if io_dir is not None and not os.path.exists(io_dir):
            os.makedirs(io_dir)

    # Get the list of files
    image_filenames = os.listdir(input_to_process_images_dir)
    random.shuffle(image_filenames)

    # Split the processed
    train_split = int(len(image_filenames) * train_ratio)
    val_split = int(len(image_filenames) * val_ratio)

    # Copy the files to the output directories
    for i, image_filename in enumerate(image_filenames):
        # Get the image and annotations paths
        input_to_process_image_path = os.path.join(input_to_process_images_dir, image_filename)
        annotations_filename = os.path.splitext(image_filename)[0] + '.txt'
        input_to_process_annotations_path = os.path.join(input_to_process_annotations_dir, annotations_filename)

        if i < train_split:
            copy_file(input_to_process_image_path, output_organized_training_images_dir)
            copy_file(input_to_process_annotations_path, output_organized_training_annotations_dir)
        elif i < train_split + val_split:
            copy_file(input_to_process_image_path, output_organized_validations_images_dir)
            copy_file(input_to_process_annotations_path, output_organized_validations_annotations_dir)
        else:
            copy_file(input_to_process_image_path, output_organized_testing_images_dir)
            copy_file(input_to_process_annotations_path, output_organized_testing_annotations_dir)

        # Log
        print(f'Copied {image_filename} to the respective directories')

    # Move the folders to the processed directory
    if output_processed_dir is not None:
        move_folder(input_to_process_images_dir, output_processed_images_dir)
        move_folder(input_to_process_annotations_dir, output_processed_annotations_dir)