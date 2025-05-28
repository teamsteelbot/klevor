import cv2
import matplotlib.pyplot as plt
import numpy as np
from opencv import DEFAULT_SIZE, DEFAULT_COLOR
from model.image_bounding_boxes import ImageBoundingBoxes
from utils import check_type


class Detections:
    """
    Class for handling detections in images.
    """

    @staticmethod
    def draw_detection(labels: list, image: np.ndarray, box: list, image_bounding_boxes: ImageBoundingBoxes, scale_factor: float):
        """
        Draw box and label for one detection.

        Args:
            image (np.ndarray): Image to draw on.
            box (list): Bounding box coordinates.
            scale_factor (float): Scale factor for coordinates.
        """
        # Check type of image bounding boxes
        check_type(image_bounding_boxes, ImageBoundingBoxes)

        label = f"{labels[cls]}: {score:.2f}%"
        ymin, xmin, ymax, xmax = box
        ymin, xmin, ymax, xmax = int(ymin * scale_factor), int(xmin * scale_factor), int(ymax * scale_factor), int(
            xmax * scale_factor)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, label, (xmin + 4, ymin + 20), font, 0.5, color, 1, cv2.LINE_AA)


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

    @staticmethod
    def draw_detections(detections: dict, image: np.ndarray, min_score: float = 0.45, scale_factor: float = 1):
        """
        Draw detections on the image.

        Args:
            detections (dict): Detection results containing 'detection_boxes', 'detection_classes', 'detection_scores', and 'num_detections'.
            image (np.ndarray): Image to draw on.
            min_score (float): Minimum score threshold. Defaults to 0.45.
            scale_factor (float): Scale factor for coordinates. Defaults to 1.

        Returns:
            np.ndarray: Image with detections drawn.
        """
        boxes = detections['detection_boxes']
        classes = detections['detection_classes']
        scores = detections['detection_scores']

        # Values used for scaling coords and removing padding
        img_height, img_width = image.shape[:2]
        size = max(img_height, img_width)
        padding_length = int(abs(img_height - img_width) / 2)

        for idx in range(detections['num_detections']):
            if scores[idx] >= min_score:
                color = generate_color(classes[idx])
                scaled_box = self.denormalize_and_remove_padding(boxes[idx], size, padding_length, img_height, img_width)
                self.draw_detection(image, scaled_box, classes[idx], scores[idx] * 100.0, color, scale_factor)

        return image