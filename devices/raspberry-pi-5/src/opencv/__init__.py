import os
import random
import time
from typing import Optional

from PIL.Image import Image
import cv2
import numpy as np

from .constants import COLOR, MAX_CALIB_SET_SAMPLES, SHAPE
from ..args import Args
from ..constants import MODELS_COLORS, SIZE
from ..files import Files
from ..utils import is_instance


class OpenCV:
    """
    OpenCV utility class for image processing.
    """

    @staticmethod
    def resize_image(
        image: np.ndarray,
        size: tuple[int, int] = (SIZE, SIZE),
        interpolation=cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Resize an image to the specified size.

        Args:
            image (np.ndarray): Image to resize.
            size (tuple[int, int): Desired size (width, height).
            interpolation: Interpolation method used for resizing.
        Returns:
            np.ndarray: Resized image.
        """
        return cv2.resize(
            image,
            size,
            interpolation=interpolation
        ) if size else image

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
    def get_rgb_color(
        cls,
        class_number: int,
        rgb_colors: tuple[tuple[int, int, int]] = None
    ) -> tuple[int, int, int]:
        """
        Get RGB color.

        Args:
            class_number (int): Class number.
            rgb_colors (tuple[tuple[int, int, int]], optional): Tuple mapping class indices to RGB colors.
        Returns:
            tuple[int, int, int]: RGB color tuple for the class number.
        """
        return rgb_colors[
            class_number] if rgb_colors is not None and class_number in rgb_colors else COLOR

    @classmethod
    def get_bgr_color(
        cls,
        class_number: int,
        rgb_colors: tuple[tuple[int, int, int]] = None
    ) -> tuple:
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
    def load_image(
        cls,
        image_path: str,
        image_size: tuple[int, int] = None,
        to_rgb: bool = True,
        interpolation=cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Load an image from a file.

        Args:
            image_path (str): Path to the image file.
            image_size (tuple[int, int]): Size to resize the image to.
            to_rgb (bool): Whether to convert the image to RGB format.
            interpolation: Interpolation method used for resizing.
        Returns:
            np.ndarray: Loaded image.
        Raises:
            ValueError: If the image path is invalid or the image cannot be loaded.
        """
        # Check the type of image path
        is_instance(image_path, str)

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
    def preprocess(
        cls,
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Preprocess the image.

        Args:
            image (np.ndarray): Image to preprocess.
        Returns:
            np.ndarray: Preprocessed image tensor.
        """
        # Normalize the image and transpose it
        image_normalized = image.astype(np.float32) / 255.0
        image_transposed = np.transpose(image_normalized, (2, 0, 1))

        # Expand the dimensions
        image_expanded = np.expand_dims(image_transposed, axis=0)
        return image_expanded

    @classmethod
    def load_and_preprocess_image(
        cls,
        image_path: str | os.PathLike[str],
        image_size: tuple[int, int] = (SIZE, SIZE),
        to_rgb: bool = True,
        interpolation=cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Load and preprocess an image.

        Args:
            image_path (str|os.PathLike[str]): Path to the image file.
            image_size (tuple[int, int]): Size to resize the image to.
            to_rgb (bool): Whether to convert the image to RGB format.
            interpolation: Interpolation method used for resizing.
        Returns:
            tuple[np.ndarray, np.ndarray]: Original image and preprocessed image tensor.
        """
        # Load the image
        original_image = cls.load_image(
            image_path, image_size, to_rgb, interpolation
            )

        # Resize the image and convert it to RGB
        return cls.preprocess(original_image)

    @classmethod
    def preprocess_pil_image(
        cls,
        image: Image,
    ) -> np.ndarray:
        """
        Preprocess a PIL image.

        Args:
            image (Image): PIL image to preprocess.
        Returns:
            np.ndarray: Preprocessed image tensor.
        """
        # Check the type of image
        is_instance(image, Image)

        # Convert the PIL image to a numpy array
        image_np = np.array(image)

        # Resize the image and convert it to RGB
        return cls.preprocess(image_np)

    @classmethod
    def resize_images(
        cls,
        input_to_process_dir: str | os.PathLike[str],
        output_resized_to_process_dir: str | os.PathLike[str],
        output_processed_dir: Optional[str | os.PathLike[str]] = None,
        new_image_size: tuple[int, int] = SIZE,
        interpolation=cv2.INTER_LINEAR
    ) -> None:
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
                image = cls.load_image(
                    image_path, new_image_size,
                    interpolation=interpolation
                    )

                # Write back the image
                output_path = os.path.join(
                    output_resized_to_process_dir,
                    filename
                    )
                cv2.imwrite(output_path, image)

                # End timing
                end_time = time.time()
                elapsed_time = end_time - start_time

                # Log
                print(
                    f'Resized and saved {filename} to {output_resized_to_process_dir} in {elapsed_time:.2f} seconds'
                )

                # Check if the output_processed_dir is not None
                if not output_processed_dir:
                    Files.move_file(
                        image_path,
                        os.path.join(
                            output_processed_dir,
                            filename
                            )
                        )

    @classmethod
    def preprocess_images_to_npy(
        cls,
        input_folder: str | os.PathLike[str],
        output_file: str | os.PathLike[str],
        target_shape: tuple = SHAPE
    ) -> None:
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
        if calib_size <= MAX_CALIB_SET_SAMPLES:
            image_files = enumerate(os.listdir(input_folder))
        else:
            calib_size = MAX_CALIB_SET_SAMPLES
            image_files = enumerate(
                random.sample(os.listdir(input_folder), MAX_CALIB_SET_SAMPLES)
            )
        h, w, c = target_shape

        # Initialize an empty array to store preprocessed images
        images_array = np.zeros((calib_size, h, w, c), dtype=np.uint8)

        # Iterate through each image in the input folder
        counter = 0
        for _, image_name in image_files:
            image_path = os.path.join(input_folder, image_name)
            image = cls.load_image(
                image_path, image_size=(w, h), to_rgb=True,
                interpolation=cv2.INTER_LINEAR
                )

            # Add the preprocessed image to the array
            images_array[counter] = image
            counter += 1

        # Save the array to a .npy file
        np.save(output_file, images_array)
        print(f"Saved preprocessed images to {output_file}")

    @staticmethod
    def get_model_classes_color_palette(
        model_name: str
    ) -> tuple[tuple[int, int, int]]:
        """
        Get the model classes color palette.

        Args:
            model_name (str): Name of the YOLO model.
        Returns:
            tuple[tuple[int, int, int]]: Tuple mapping class indices to RGB color tuples.
        Raises:
            ValueError: If the model name does not have a defined color palette.
        """
        # Check the validity of the model name
        Args.check_model_name(model_name)

        if not model_name in MODELS_COLORS:
            raise ValueError(
                f"Model name '{model_name}' does not have a defined color palette."
            )
        return MODELS_COLORS[model_name]
