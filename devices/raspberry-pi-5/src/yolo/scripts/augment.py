import os
import shutil
from argparse import ArgumentParser
from time import time
from typing import Optional

import cv2
from albumentations import (
    BboxParams,
    Compose,
    HorizontalFlip,
    RandomBrightnessContrast,
    RandomCrop,
    ShiftScaleRotate,
)

from ..args import Args, Flag
from ..constants import IMAGE_EXTENSIONS, NUM_AUGMENTATIONS
from ..files import Files
from ..files.constants import (
    DATASET_AUGMENTED,
    DATASET_IMAGES,
    DATASET_LABELED,
    DATASET_LABELS,
    DATASET_PROCESSED,
    DATASET_TO_PROCESS,
)
from ...opencv import OpenCV


def augment_image(
    input_to_process_image_path: str | os.PathLike[str],
    input_to_process_annotations_path: str | os.PathLike[str],
    output_augmented_images_dir: str | os.PathLike[str],
    output_augmented_annotations_dir: str | os.PathLike[str],
    num_augmentations: int,
    output_processed_images_dir: Optional[str | os.PathLike[str]] = None,
    output_processed_annotations_dir: Optional[str | os.PathLike[str]] = None,
) -> None:
    """
    Augment to process image.

    Args:
        input_to_process_image_path (str|os.PathLike[str]): Path to the image to be augmented.
        input_to_process_annotations_path (str|os.PathLike[str]): Path to the annotations for the image.
        output_augmented_images_dir (str|os.PathLike[str]): Directory where the augmented images will be saved.
        output_augmented_annotations_dir (str|os.PathLike[str]): Directory where the augmented annotations will be saved.
        num_augmentations (int): Number of augmentations to perform on the image.
        output_processed_images_dir (Optional[str|os.PathLike[str]]): Directory where the original image will be moved after processing.
        output_processed_annotations_dir (Optional[str|os.PathLike[str]]): Directory where the original annotations will be moved after processing.
    """
    # Get current time
    start_time = time()

    # Read the image and convert it to RGB
    image = OpenCV.load_image(input_to_process_image_path)

    # Read the annotations
    with open(input_to_process_annotations_path, 'r') as f:
        lines = f.readlines()

    # Parse the annotations
    bboxes = []
    class_labels = []
    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center, y_center, width, height = map(float, parts[1:])
        bboxes.append([x_center, y_center, width, height])
        class_labels.append(class_id)

    # Define the pipeline
    transform = Compose(
        [
            # Apply with a 50% probability a random brightness and contrast adjustment
            RandomBrightnessContrast(p=0.5),

            # Apply with a 50% probability a horizontal flip
            HorizontalFlip(p=0.5),

            # Apply with a 50% probability a random shift, scale, and rotation
            ShiftScaleRotate(
                shift_limit=0.2, scale_limit=0.2, rotate_limit=25,
                p=0.5
                ),

            # Apply with a 30% probability a random RGB shift
            # RGBShift(r_shift_limit=25, g_shift_limit=25, b_shift_limit=25, p=0.3),
            # Currently, this is being on hold because it may trigger incorrect labels due to the color shift

            # Apply with a 30% probability a random crop
            RandomCrop(
                width=int(image.shape[1] * 0.9),
                height=int(image.shape[0] * 0.9), p=0.3
                ),
        ], bbox_params=BboxParams(format='yolo', label_fields=['class_labels'])
    )

    # Apply the pipeline to the image and annotations
    try:
        for i in range(num_augmentations):
            transformed = transform(
                image=image, bboxes=bboxes,
                class_labels=class_labels
                )
            transformed_image = transformed['image']
            transformed_bboxes = transformed['bboxes']
            transformed_class_labels = transformed['class_labels']

            # Save the image and annotations
            output_image_path = os.path.join(
                output_augmented_images_dir,
                f"{os.path.splitext(os.path.basename(input_to_process_image_path))[0]}_aug_{i}.jpg"
                )
            output_annotations_path = os.path.join(
                output_augmented_annotations_dir,
                f"{os.path.splitext(os.path.basename(input_to_process_annotations_path))[0]}_aug_{i}.txt"
            )

            # Convert the image back to BGR and save it
            cv2.imwrite(
                output_image_path,
                cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR)
                )

            # Log the image
            end_time = time()
            elapsed_time = end_time - start_time
            print(
                f"Augmented image saved to {output_image_path} in {elapsed_time:.2f} seconds"
            )

            # Save the annotations
            with open(output_annotations_path, 'w') as f:
                for j, bbox in enumerate(transformed_bboxes):
                    class_id = transformed_class_labels[j]
                    x_center, y_center, width, height = bbox
                    f.write(
                        f"{class_id} {x_center} {y_center} {width} {height}\n"
                    )

            # Log annotations
            end_time = time()
            elapsed_time = end_time - start_time
            print(
                f"Augmented annotations saved to {output_annotations_path} in {elapsed_time:.2f} seconds"
            )

            # Check if the output_processed_images_dir is not None
            if output_processed_images_dir:
                Files.move_file(
                    input_to_process_image_path,
                    output_processed_images_dir
                    )

            # Check if the output_processed_annotations_dir is not None
            if output_processed_annotations_dir:
                Files.move_file(
                    input_to_process_annotations_path,
                    output_processed_annotations_dir
                    )

    except Exception as e:
        print(f"Error: {e} for {input_to_process_image_path}")


def augment_dataset(
    input_to_process_dir: str | os.PathLike[str],
    output_augmented_dir: str | os.PathLike[str],
    num_augmentations: int = NUM_AUGMENTATIONS,
    output_processed_dir: Optional[str | os.PathLike[str]] = None
):
    """
    Augment a dataset.

    Args:
        input_to_process_dir (str | os.PathLike[str]): Directory containing the images and annotations to be augmented.
        output_augmented_dir (str | os.PathLike[str]): Directory where the augmented images and annotations will be saved.
        num_augmentations (int): Number of augmentations to perform on each image.
        output_processed_dir (Optional[str | os.PathLike[str]]): Directory where the original images and annotations will be moved after processing.
    """
    # Get the input images and annotations directories
    input_to_process_images_dir = os.path.join(
        input_to_process_dir,
        DATASET_IMAGES
        )
    input_to_process_annotations_dir = os.path.join(
        input_to_process_dir,
        DATASET_LABELS
        )

    # Get the output directories
    output_augmented_images_dir = os.path.join(
        output_augmented_dir,
        DATASET_IMAGES
        )
    output_augmented_annotations_dir = os.path.join(
        output_augmented_dir,
        DATASET_LABELS
        )
    output_processed_images_dir = os.path.join(
        output_processed_dir,
        DATASET_IMAGES
        )
    output_processed_annotations_dir = os.path.join(
        output_processed_dir,
        DATASET_LABELS
        )

    # Check if the output directories exist, if not it creates them
    for io_dir in [input_to_process_dir, input_to_process_images_dir,
                   input_to_process_annotations_dir,
                   output_augmented_dir, output_augmented_images_dir,
                   output_augmented_annotations_dir,
                   output_processed_images_dir,
                   output_processed_annotations_dir]:
        Files.ensure_directory_exists(io_dir)

    # Get the image files
    image_filenames = [f for f in os.listdir(input_to_process_images_dir) if
                       f.lower().endswith(IMAGE_EXTENSIONS)]

    # Augment each image
    for image_filename in image_filenames:
        print(f"Augmenting {image_filename}")

        # Get the image and annotations paths
        input_to_process_image_path = os.path.join(
            input_to_process_images_dir,
            image_filename
            )
        annotations_filename = os.path.splitext(image_filename)[0] + '.txt'
        input_to_process_annotations_path = os.path.join(
            input_to_process_annotations_dir, annotations_filename
        )

        if os.path.exists(input_to_process_annotations_dir):
            augment_image(
                input_to_process_image_path,
                input_to_process_annotations_path,
                output_augmented_images_dir,
                output_augmented_annotations_dir,
                num_augmentations,
                output_processed_images_dir,
                output_processed_annotations_dir, )
        else:
            print(
                f"Warning: Annotation file not found for {input_to_process_image_path}, annotation file should be at {input_to_process_annotations_path}"
            )

    # Remove the input images and annotations folders
    shutil.rmtree(input_to_process_images_dir)
    shutil.rmtree(input_to_process_annotations_dir)


if __name__ == '__main__':
    parser = ArgumentParser(description='Script to augment YOLO model')
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
    labeled_processed_dir = Files.get_dataset_model_dir_path(
        DATASET_LABELED,
        DATASET_PROCESSED,
        arg_yolo_input_model
        )
    augmented_dir = Files.get_dataset_model_dir_path(
        DATASET_AUGMENTED, None,
        arg_yolo_input_model
        )

    # Augment the dataset
    augment_dataset(
        labeled_to_process_dir, augmented_dir, NUM_AUGMENTATIONS,
        labeled_processed_dir
        )
