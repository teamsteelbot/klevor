from argparse import ArgumentParser
import os
import shutil

from opencv.augmentation import augment_image
from yolo import Yolo
from yolo.args import Args
from yolo.files import Files


def augment_dataset(input_to_process_dir: str, output_augmented_dir: str, num_augmentations=Yolo.NUM_AUGMENTATIONS,
                    output_processed_dir: str = None):
    """
    Augment a dataset.

    Args:
        input_to_process_dir (str): Directory containing the images and annotations to be augmented.
        output_augmented_dir (str): Directory where the augmented images and annotations will be saved.
        num_augmentations (int): Number of augmentations to perform on each image.
        output_processed_dir (str, optional): Directory where the original images and annotations will be moved after processing.

    Returns:
        None
    """
    # Get the input images and annotations directories
    input_to_process_images_dir = os.path.join(input_to_process_dir, Files.DATASET_IMAGES)
    input_to_process_annotations_dir = os.path.join(input_to_process_dir, Files.DATASET_LABELS)

    # Get the output directories
    output_augmented_images_dir = os.path.join(output_augmented_dir, Files.DATASET_IMAGES)
    output_augmented_annotations_dir = os.path.join(output_augmented_dir, Files.DATASET_LABELS)
    output_processed_images_dir = os.path.join(output_processed_dir, Files.DATASET_IMAGES)
    output_processed_annotations_dir = os.path.join(output_processed_dir, Files.DATASET_LABELS)

    # Check if the output directories exist, if not it creates them
    for io_dir in [input_to_process_dir, input_to_process_images_dir, input_to_process_annotations_dir,
                   output_augmented_dir, output_augmented_images_dir,
                   output_augmented_annotations_dir,
                   output_processed_images_dir, output_processed_annotations_dir]:
        Files.ensure_directory_exists(io_dir)

    # Get the image files
    image_filenames = [f for f in os.listdir(input_to_process_images_dir) if
                       f.lower().endswith(Yolo.IMAGE_EXTENSIONS)]

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
    parser = ArgumentParser(description='Script to augment YOLO model')
    Args.add_yolo_input_model_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args(args, Args.INPUT_MODEL)

    # Get the dataset paths
    labeled_to_process_dir = Files.get_dataset_model_dir_path(Files.DATASET_LABELED, Files.DATASET_TO_PROCESS,
                                                              arg_yolo_input_model)
    labeled_processed_dir = Files.get_dataset_model_dir_path(Files.DATASET_LABELED, Files.DATASET_PROCESSED,
                                                             arg_yolo_input_model)
    augmented_dir = Files.get_dataset_model_dir_path(Files.DATASET_AUGMENTED, None, arg_yolo_input_model)

    # Augment the dataset
    augment_dataset(labeled_to_process_dir, augmented_dir, Yolo.NUM_AUGMENTATIONS, labeled_processed_dir)


if __name__ == '__main__':
    main()
