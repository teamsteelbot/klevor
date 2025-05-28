import argparse
import os
import shutil

from args import get_attribute_from_args, parse_args_as_dict
from files import ensure_path_exists
from opencv.augmentation import augment_image
from yolo import (YOLO_NUM_AUGMENTATIONS, ARGS_YOLO_INPUT_MODEL,
                  YOLO_DATASET_LABELED, YOLO_DATASET_AUGMENTED, YOLO_DATASET_TO_PROCESS, YOLO_DATASET_PROCESSED,
                  YOLO_DATASET_IMAGES, YOLO_DATASET_LABELS, IMAGE_EXTENSIONS)
from yolo.args import add_yolo_input_model_argument
from yolo.files import get_dataset_model_dir_path


def augment_dataset(input_to_process_dir: str, output_augmented_dir: str, num_augmentations=5,
                    output_processed_dir: str = None):
    """
    Augment a dataset.
    """
    # Get the input images and annotations directories
    input_to_process_images_dir = os.path.join(input_to_process_dir, YOLO_DATASET_IMAGES)
    input_to_process_annotations_dir = os.path.join(input_to_process_dir, YOLO_DATASET_LABELS)

    # Get the output directories
    output_augmented_images_dir = os.path.join(output_augmented_dir, YOLO_DATASET_IMAGES)
    output_augmented_annotations_dir = os.path.join(output_augmented_dir, YOLO_DATASET_LABELS)
    output_processed_images_dir = os.path.join(output_processed_dir, YOLO_DATASET_IMAGES)
    output_processed_annotations_dir = os.path.join(output_processed_dir, YOLO_DATASET_LABELS)

    # Check if the output directories exist, if not it creates them
    for io_dir in [input_to_process_dir, input_to_process_images_dir, input_to_process_annotations_dir,
                   output_augmented_dir, output_augmented_images_dir,
                   output_augmented_annotations_dir,
                   output_processed_images_dir, output_processed_annotations_dir]:
        ensure_path_exists(io_dir)

    # Get the image files
    image_filenames = [f for f in os.listdir(input_to_process_images_dir) if
                       f.lower().endswith(IMAGE_EXTENSIONS)]

    # Augment each image
    for image_filename in image_filenames:
        print(f"Augmenting {image_filename}")

        # Get the image and annotations paths
        input_to_process_image_path = os.path.join(input_to_process_images_dir, image_filename)
        annotations_filename = os.path.splitext(image_filename)[0] + '.txt'
        input_to_process_annotations_path = os.path.join(input_to_process_annotations_dir, annotations_filename)

        if os.path.exists(input_to_process_annotations_dir):
            augment_image(input_to_process_image_path, input_to_process_annotations_path,
                          output_augmented_images_dir,
                          output_augmented_annotations_dir, output_processed_images_dir,
                          output_processed_annotations_dir)
        else:
            print(
                f"Warning: Annotation file not found for {input_to_process_image_path}, annotation file should be at {input_to_process_annotations_path}")

    # Remove the input images and annotations folders
    shutil.rmtree(input_to_process_images_dir)
    shutil.rmtree(input_to_process_annotations_dir)

def main():
    """
    Main function to run the script.
    """
    parser = argparse.ArgumentParser(description='Script to augment YOLO model')
    add_yolo_input_model_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the dataset paths
    labeled_to_process_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_TO_PROCESS,
                                                        arg_yolo_input_model)
    labeled_processed_dir = get_dataset_model_dir_path(YOLO_DATASET_LABELED, YOLO_DATASET_PROCESSED,
                                                       arg_yolo_input_model)
    augmented_dir = get_dataset_model_dir_path(YOLO_DATASET_AUGMENTED, None, arg_yolo_input_model)

    # Augment the dataset
    augment_dataset(labeled_to_process_dir, augmented_dir, YOLO_NUM_AUGMENTATIONS, labeled_processed_dir)

if __name__ == '__main__':
    main()