import os
import time

import albumentations as A
import cv2

from files import Files
from opencv import AUGMENTATION_SAMPLES
from opencv.preprocessing import Preprocessing


def augment_image(input_to_process_image_path: str, input_to_process_annotations_path: str,
                  output_augmented_images_dir: str, output_augmented_annotations_dir: str,
                  output_processed_images_dir: str = None, output_processed_annotations_dir: str = None,
                  num_augmentations=AUGMENTATION_SAMPLES) -> None:
    """
    Augment to process image.

    Args:
        input_to_process_image_path (str): Path to the image to be augmented.
        input_to_process_annotations_path (str): Path to the annotations for the image.
        output_augmented_images_dir (str): Directory where the augmented images will be saved.
        output_augmented_annotations_dir (str): Directory where the augmented annotations will be saved.
        num_augmentations (int): Number of augmentations to perform on the image.
        output_processed_images_dir (str, optional): Directory where the original image will be moved after processing.
        output_processed_annotations_dir (str, optional): Directory where the original annotations will be moved after processing.
    """
    # Get current time
    start_time = time.time()

    # Read the image and convert it to RGB
    image = Preprocessing.load_image(input_to_process_image_path, )

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
    transform = A.Compose([
        # Apply with a 50% probability a random brightness and contrast adjustment
        A.RandomBrightnessContrast(p=0.5),

        # Apply with a 50% probability a horizontal flip
        A.HorizontalFlip(p=0.5),

        # Apply with a 50% probability a random shift, scale, and rotation
        A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.2, rotate_limit=25, p=0.5),

        # Apply with a 30% probability a random RGB shift
        # A.RGBShift(r_shift_limit=25, g_shift_limit=25, b_shift_limit=25, p=0.3),
        # Currently, this is being on hold because it may trigger incorrect labels due to the color shift

        # Apply with a 30% probability a random crop
        A.RandomCrop(width=int(image.shape[1] * 0.9), height=int(image.shape[0] * 0.9), p=0.3),  # Optional random crop
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

    # Apply the pipeline to the image and annotations
    try:
        for i in range(num_augmentations):
            transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            transformed_image = transformed['image']
            transformed_bboxes = transformed['bboxes']
            transformed_class_labels = transformed['class_labels']

            # Save the image and annotations
            output_image_path = os.path.join(output_augmented_images_dir,
                                             f"{os.path.splitext(os.path.basename(input_to_process_image_path))[0]}_aug_{i}.jpg")
            output_annotations_path = os.path.join(output_augmented_annotations_dir,
                                                   f"{os.path.splitext(os.path.basename(input_to_process_annotations_path))[0]}_aug_{i}.txt")

            # Convert the image back to BGR and save it
            cv2.imwrite(output_image_path, cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))

            # Log the image
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Augmented image saved to {output_image_path} in {elapsed_time:.2f} seconds")

            # Save the annotations
            with open(output_annotations_path, 'w') as f:
                for j, bbox in enumerate(transformed_bboxes):
                    class_id = transformed_class_labels[j]
                    x_center, y_center, width, height = bbox
                    f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

            # Log annotations
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Augmented annotations saved to {output_annotations_path} in {elapsed_time:.2f} seconds")

            # Check if the output_processed_images_dir is not None
            if output_processed_images_dir:
                Files.move_file(input_to_process_image_path, output_processed_images_dir)

            # Check if the output_processed_annotations_dir is not None
            if output_processed_annotations_dir:
                Files.move_file(input_to_process_annotations_path, output_processed_annotations_dir)

    except Exception as e:
        print(f"Error: {e} for {input_to_process_image_path}")
