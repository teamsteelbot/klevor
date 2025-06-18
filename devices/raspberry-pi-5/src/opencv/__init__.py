import random
import os
import time
from typing import Optional

import matplotlib as plt
import cv2
import numpy as np
import albumentations as A

from ..files import Files
from ..utils import check_type

class OpenCV:
    # Image dimensions
    WIDTH = 640
    HEIGHT = 640
    SIZE = (WIDTH, HEIGHT)
    CHANNELS = 3
    SHAPE = (HEIGHT, WIDTH, CHANNELS)

    # Color
    COLOR = (0, 255, 0)

    # Unused color
    UNUSED_COLOR = (255, 255, 255)

    # Calibration set
    MAX_CALIB_SET_SAMPLES = 100

    # Number of augmentation samples
    AUGMENTATION_SAMPLES = 10

    @staticmethod
    def resize_image(image: np.ndarray, size: tuple = SIZE, interpolation=cv2.INTER_LINEAR) -> np.ndarray:
        """
        Resize an image to the specified size.

        Args:
            image (np.ndarray): Image to resize.
            size (tuple): Desired size (width, height).
            interpolation: Interpolation method used for resizing.

        Returns:
            np.ndarray: Resized image.
        """
        return cv2.resize(image, size, interpolation=interpolation) if size else image

    @staticmethod
    def rgb_to_bgr(rgb: tuple[int, int, int]) -> tuple:
        """
        Convert RGB to BGR.

        Args:
            rgb (tuple[int, int, int]): RGB color tuple.
        Returns:
            tuple: BGR color tuple.
        """
        return rgb[::-1]

    @classmethod
    def get_rgb_color(cls, class_number: int, rgb_colors: tuple[tuple[int, int, int]] = None) -> tuple[
        int, int, int]:
        """
        Get RGB color.

        Args:
            class_number (int): Class number.
            rgb_colors (tuple[tuple[int, int, int]], optional): Tuple mapping class indices to RGB colors.
        Returns:
            tuple[int, int, int]: RGB color tuple for the class number.
        """
        return rgb_colors[class_number] if rgb_colors is not None and class_number in rgb_colors else cls.COLOR

    @classmethod
    def get_bgr_color(cls, class_number: int, rgb_colors: tuple[tuple[int, int, int]] = None) -> tuple:
        """
        Get BGR color.

        Args:
            class_number (int): Class number.
            rgb_colors (tuple[tuple[int, int, int]], optional): Tuple mapping class indices to RGB colors.
        Returns:
            tuple[int, int, int]: BGR color tuple for the class number.
        """
        return cls.rgb_to_bgr(cls.get_rgb_color(class_number, rgb_colors))

    @classmethod
    def load_image(cls, image_path: str, image_size: tuple[int, int] = None, to_rgb: bool = True,
                   interpolation=cv2.INTER_LINEAR) -> np.ndarray:
        """
        Load an image from a file.

        Args:
            image_path (str): Path to the image file.
            image_size (tuple[int, int]): Size to resize the image to, default is None.
            to_rgb (bool): Whether to convert the image to RGB format, default is True.
            interpolation: Interpolation method used for resizing.
        Returns:
            np.ndarray: Loaded image.
        """
        # Check the type of image path
        check_type(image_path, str)

        # Check if the image path exists
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Image at {image_path} could not be loaded.")

        # Resize the image if image_size is specified
        image = cls.resize_image(image, image_size, interpolation)

        # Convert the image to RGB if specified
        if to_rgb:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return image

    @classmethod
    def preprocess(cls, image_path: str, image_size: tuple[int, int] = SIZE) -> tuple:
        """
        Preprocess the image.

        Args:
            image_path (str): Path to the image file.
            image_size (tuple[int, int]): Size to resize the image to, default is SIZE.
        Returns:
            tuple: Original image and preprocessed image tensor.
        """
        # Resize the image and convert it to RGB
        image = cls.load_image(image_path, image_size)

        # Normalize the image and transpose it
        image_normalized = image.astype(np.float32) / 255.0
        image_transposed = np.transpose(image_normalized, (2, 0, 1))

        # Expand the dimensions
        image_expanded = np.expand_dims(image_transposed, axis=0)
        return image, image_expanded

    @classmethod
    def resize_images(cls, input_to_process_dir: str | os.PathLike[str], output_resized_to_process_dir: str | os.PathLike[str],
                     output_processed_dir: Optional[str | os.PathLike[str]] = None, new_image_size: tuple[int, int] = SIZE,
                     interpolation=cv2.INTER_LINEAR) -> None:
        """
        Resize images function.

        Args:
            input_to_process_dir (str|os.PathLike[str]): Directory containing images to be resized.
            output_resized_to_process_dir (str|os.PathLike[str]): Directory where resized images will be saved.
            new_image_size (tuple[int, int]): New size for the images as (width, height).
            output_processed_dir (Optional[str|os.PathLike[str]]): Directory where original images will be moved after processing.
            interpolation: Interpolation method used for resizing.
        """
        # Check if the path exists, if not it creates it
        Files.ensure_directory_exists(output_resized_to_process_dir)

        # Iterate over the files in the given path
        for filename in os.listdir(input_to_process_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                # Start timing
                start_time = time.time()

                # Read image
                image_path = os.path.join(input_to_process_dir, filename)
                image = cls.load_image(image_path, new_image_size, interpolation=interpolation)

                # Write back the image
                output_path = os.path.join(output_resized_to_process_dir, filename)
                cv2.imwrite(output_path, image)

                # End timing
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Log
                print(f'Resized and saved {filename} to {output_resized_to_process_dir} in {elapsed_time:.2f} seconds')

                # Check if the output_processed_dir is not None
                if not output_processed_dir:
                    Files.move_file(image_path, os.path.join(output_processed_dir, filename))

    @classmethod
    def augment_image(cls, input_to_process_image_path: str | os.PathLike[str], input_to_process_annotations_path: str | os.PathLike[str],
                      output_augmented_images_dir: str | os.PathLike[str], output_augmented_annotations_dir: str | os.PathLike[str],
                      output_processed_images_dir: Optional[str | os.PathLike[str]] = None,
                      output_processed_annotations_dir: Optional[str | os.PathLike[str]] = None, num_augmentations=AUGMENTATION_SAMPLES) -> None:
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
        start_time = time.time()

        # Read the image and convert it to RGB
        image = cls.load_image(input_to_process_image_path)

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
            A.RandomCrop(width=int(image.shape[1] * 0.9), height=int(image.shape[0] * 0.9), p=0.3),
            # Optional random crop
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


    @classmethod
    def preprocess_images_to_npy(cls, input_folder: str | os.PathLike[str],
                                 output_file: str | os.PathLike[str], target_shape: tuple = SHAPE) -> None:
        """
        Preprocess images from a folder and save them as a .npy file.

        Args:
            input_folder (str|os.PathLike[str]): Path to the folder containing images.
            output_file (str|os.PathLike[str]): Path where the .npy file will be saved.
            target_shape (tuple): Desired shape of the images (height, width, channels).
        """
        # Ensure the output directory exists
        Files.ensure_directory_exists(output_file)

        # Get the images
        calib_size = len(os.listdir(input_folder))  # Number of images
        if calib_size <= cls.MAX_CALIB_SET_SAMPLES:
            image_files = enumerate(os.listdir(input_folder))
        else:
            calib_size = cls.MAX_CALIB_SET_SAMPLES
            image_files = enumerate(random.sample(os.listdir(input_folder), cls.MAX_CALIB_SET_SAMPLES))
        h, w, c = target_shape

        # Initialize an empty array to store preprocessed images
        images_array = np.zeros((calib_size, h, w, c), dtype=np.uint8)

        # Iterate through each image in the input folder
        counter = 0
        for _, image_name in image_files:
            image_path = os.path.join(input_folder, image_name)
            image = cls.load_image(image_path, image_size=(w, h), to_rgb=True, interpolation=cv2.INTER_LINEAR)

            # Add the preprocessed image to the array
            images_array[counter] = image
            counter += 1

        # Save the array to a .npy file
        np.save(output_file, images_array)
        print(f"Saved preprocessed images to {output_file}")