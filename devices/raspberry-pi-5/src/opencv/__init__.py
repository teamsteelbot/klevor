import random
import os
import time
from typing import LiteralString, Optional

import matplotlib as plt
import cv2
import numpy as np
import albumentations as A

from ..files import Files
from ..utils import check_type
from ..yolo.image_bounding_boxes import ImageBoundingBoxes

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

    @classmethod
    def resize_images(cls, input_to_process_dir: LiteralString | str | bytes, output_resized_to_process_dir: LiteralString | str | bytes,
                     output_processed_dir: Optional[LiteralString | str | bytes] = None, new_image_size: tuple[int, int] = SIZE,
                     interpolation=cv2.INTER_LINEAR) -> None:
        """
        Resize images function.

        Args:
            input_to_process_dir (LiteralString|str|bytes): Directory containing images to be resized.
            output_resized_to_process_dir (LiteralString|str|bytes): Directory where resized images will be saved.
            new_image_size (tuple[int, int]): New size for the images as (width, height).
            output_processed_dir (Optional[LiteralString|str|bytes]): Directory where original images will be moved after processing.
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
    def augment_image(cls, input_to_process_image_path: LiteralString | str | bytes, input_to_process_annotations_path: LiteralString | str | bytes,
                      output_augmented_images_dir: LiteralString | str | bytes, output_augmented_annotations_dir: LiteralString | str | bytes,
                      output_processed_images_dir: Optional[LiteralString | str | bytes] = None,
                      output_processed_annotations_dir: Optional[LiteralString | str | bytes] = None, num_augmentations=AUGMENTATION_SAMPLES) -> None:
        """
        Augment to process image.

        Args:
            input_to_process_image_path (LiteralString|str|bytes): Path to the image to be augmented.
            input_to_process_annotations_path (LiteralString|str|bytes): Path to the annotations for the image.
            output_augmented_images_dir (LiteralString|str|bytes): Directory where the augmented images will be saved.
            output_augmented_annotations_dir (LiteralString|str|bytes): Directory where the augmented annotations will be saved.
            num_augmentations (int): Number of augmentations to perform on the image.
            output_processed_images_dir (Optional[LiteralString|str|bytes]): Directory where the original image will be moved after processing.
            output_processed_annotations_dir (Optional[LiteralString|str|bytes]): Directory where the original annotations will be moved after processing.
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
    def preprocess_images_to_npy(cls, input_folder: LiteralString | str | bytes,
                                 output_file: LiteralString | str | bytes, target_shape: tuple = SHAPE) -> None:
        """
        Preprocess images from a folder and save them as a .npy file.

        Args:
            input_folder (LiteralString|str|bytes): Path to the folder containing images.
            output_file (LiteralString|str|bytes): Path where the .npy file will be saved.
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

        # Font

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    @classmethod
    def draw_detection(cls, image: np.ndarray, box: list, class_name: str, score: float, color: tuple,
                       scale_factor: float):
        """
        Draw box and label for one detection.

        Args:
            image (np.ndarray): Image to draw on.
            box (list): Bounding box coordinates.
            class_name (str): Class label of the detection.
            score (float): Detection score.
            color (tuple): Color for the bounding box.
            scale_factor (float): Scale factor for coordinates.
        """
        label = f"{class_name}: {score:.2f}%"
        ymin, xmin, ymax, xmax = box
        ymin, xmin, ymax, xmax = int(ymin * scale_factor), int(xmin * scale_factor), int(ymax * scale_factor), int(
            xmax * scale_factor)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(image, label, (xmin + 4, ymin + 20), cls.FONT, 0.5, color, 1, cv2.LINE_AA)

    @staticmethod
    def denormalize_and_remove_padding(box: list, size: int, padding_length: int, input_height: int,
                                       input_width: int) -> list:
        """
        Denormalize bounding box coordinates and remove padding.

        Args:
            box (list): Normalized bounding box coordinates.
            size (int): Size to scale the coordinates.
            padding_length (int): Length of padding to remove.
            input_height (int): Height of the input image.
            input_width (int): Width of the input image.

        Returns:
            list: Denormalized bounding box coordinates with padding removed.
        """
        for i, x in enumerate(box):
            box[i] = int(x * size)
            if (input_width != size) and (i % 2 != 0):
                box[i] -= padding_length
            if (input_height != size) and (i % 2 == 0):
                box[i] -= padding_length

        return box

    @classmethod
    def draw_detections(cls, colors: dict[int, tuple[int, int, int]], image_bounding_boxes: ImageBoundingBoxes,
                        image: np.ndarray, min_score: float = 0.45, scale_factor: float = 1):
        """
        Draw detections on the image.

        Args:
            colors (dict[int, tuple[int, int, int]): Dictionary mapping class names to RGB colors.
            image_bounding_boxes (ImageBoundingBoxes): Object containing bounding boxes, classes, and scores.
            image (np.ndarray): Image to draw on.
            min_score (float): Minimum score threshold. Defaults to 0.45.
            scale_factor (float): Scale factor for coordinates. Defaults to 1.

        Returns:
            np.ndarray: Image with detections drawn.
        """
        # Values used for scaling coords and removing padding
        img_height, img_width = image.shape[:2]
        size = max(img_height, img_width)
        padding_length = int(abs(img_height - img_width) / 2)

        # Get the required values from the image bounding boxes
        boxes = image_bounding_boxes.get_xyxy()
        classes = image_bounding_boxes.get_classes()
        scores = image_bounding_boxes.get_confidences()
        for idx in range(image_bounding_boxes.get_number_of_objects()):
            if scores[idx] >= min_score:
                class_name = classes[idx]
                color = colors.get(idx, cls.UNUSED_COLOR)
                scaled_box = cls.denormalize_and_remove_padding(boxes[idx], size, padding_length, img_height, img_width)
                cls.draw_detection(image, scaled_box, class_name, scores[idx] * 100.0, color, scale_factor)

        return image

    @classmethod
    def display_detections(cls, class_names: dict[int, str], preprocessed_image: list[np.ndarray],
                           image_bounding_boxes: ImageBoundingBoxes,
                           draw_labels_name=False, font=FONT,
                           font_x_diff=0, font_y_diff=-10, font_scale=0.9, thickness=2,
                           rgb_colors: dict[int, tuple[int, int, int]] = None) -> None:
        """
        Function to display the preprocessed image and the image with detections.

        Args:
            class_names (dict[int, str]): Dictionary mapping class numbers to class names.
            preprocessed_image (list[np.ndarray]): Preprocessed image in CHW format.
            image_bounding_boxes (ImageBoundingBoxes): Object containing bounding boxes, classes, and scores.
            draw_labels_name (bool): Whether to draw class names instead of class numbers. Defaults to False.
            font (int): Font type for text. Defaults to FONT.
            font_x_diff (int): Horizontal offset for text placement. Defaults to 0.
            font_y_diff (int): Vertical offset for text placement. Defaults to -10.
            font_scale (float): Scale factor for text size. Defaults to 0.9.
            thickness (int): Thickness of bounding box and text. Defaults to 2.
            rgb_colors (dict[int, tuple[int, int, int]]): Dictionary mapping class numbers to RGB colors. Defaults to None.

        Returns:
            None: Displays the preprocessed image and the image with detections using matplotlib.
        """
        # Convert the image back to HWC format
        preprocessed_image_hwc = np.transpose(preprocessed_image[0], (1, 2, 0))

        # Convert the image to uint8
        preprocessed_image_uint8 = (preprocessed_image_hwc * 255).astype(np.uint8)

        # Display the preprocessed image
        plt.subplot(1, 2, 1)
        plt.imshow(preprocessed_image_uint8)
        plt.title('Preprocessed Image')

        # Get the image with detections
        image_with_detections = preprocessed_image_uint8.copy()

        # Draw bounding boxes with class numbers
        xyxy = image_bounding_boxes.get_xyxy()
        class_numbers = image_bounding_boxes.get_classes()
        n = image_bounding_boxes.get_number_of_objects()

        if draw_labels_name is True:
            for i in range(n):
                x1, y1, x2, y2 = xyxy[i].astype(int)
                class_number = int(class_numbers[i])
                class_name = class_names[class_number]
                color = cls.get_rgb_color(class_number, rgb_colors)
                cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(image_with_detections, class_name, (x1 + font_x_diff, y1 + font_y_diff), font, font_scale,
                            color, thickness)

        else:
            for i in range(n):
                x1, y1, x2, y2 = xyxy[i].astype(int)
                class_number = int(class_numbers[i])
                color = cls.get_rgb_color(class_number, rgb_colors)
                cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(image_with_detections, str(class_number), (x1 + font_x_diff, y1 + font_y_diff), font,
                            font_scale, color,
                            thickness)

        # Convert the image back to HWC format
        plt.subplot(1, 2, 2)
        plt.imshow(image_with_detections)
        plt.title('Image with Detections')
        plt.show()