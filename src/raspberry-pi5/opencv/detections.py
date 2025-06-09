import cv2
import numpy as np
from matplotlib import pyplot as plt

from model.image_bounding_boxes import ImageBoundingBoxes
from opencv import UNUSED_COLOR
from opencv.preprocessing import Preprocessing


class Detections:
    """
    Class for handling detections in images.
    """
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
                color = colors.get(idx, UNUSED_COLOR)
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
                color = Preprocessing.get_rgb_color(class_number, rgb_colors)
                cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(image_with_detections, class_name, (x1 + font_x_diff, y1 + font_y_diff), font, font_scale,
                            color, thickness)

        else:
            for i in range(n):
                x1, y1, x2, y2 = xyxy[i].astype(int)
                class_number = int(class_numbers[i])
                color = Preprocessing.get_rgb_color(class_number, rgb_colors)
                cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(image_with_detections, str(class_number), (x1 + font_x_diff, y1 + font_y_diff), font,
                            font_scale, color,
                            thickness)

        # Convert the image back to HWC format
        plt.subplot(1, 2, 2)
        plt.imshow(image_with_detections)
        plt.title('Image with Detections')
        plt.show()
