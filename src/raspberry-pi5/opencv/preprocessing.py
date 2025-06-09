import cv2
import numpy as np

from utils import check_type


class Preprocessing:
    """
    Class for preprocessing images.
    """
    # Image dimensions
    WIDTH = 640
    HEIGHT = 640
    SIZE = (WIDTH, HEIGHT)
    CHANNELS = 3
    SHAPE = (HEIGHT, WIDTH, CHANNELS)

    # Color
    COLOR = (0, 255, 0)

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
        if not size:
            return image

        return cv2.resize(image, size, interpolation=interpolation)

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
    def get_rgb_color(cls, class_number: int, rgb_colors: dict[int, tuple[int, int, int]] = None) -> tuple[
        int, int, int]:
        """
        Get RGB color.

        Args:
            class_number (int): Class number.
            rgb_colors (dict[int, tuple[int, int, int]], optional): Dictionary mapping class numbers to RGB colors.
        Returns:
            tuple[int, int, int]: RGB color tuple for the class number.
        """
        return rgb_colors[class_number] if rgb_colors is not None and class_number in rgb_colors else cls.COLOR

    @classmethod
    def get_bgr_color(cls, class_number: int, rgb_colors: dict[int, tuple[int, int, int]] = None) -> tuple:
        """
        Get BGR color.

        Args:
            class_number (int): Class number.
            rgb_colors (dict[int, tuple[int, int, int]], optional): Dictionary mapping class numbers to RGB colors.
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
