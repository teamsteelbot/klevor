import cv2
import matplotlib.pyplot as plt
import numpy as np
from opencv import DEFAULT_SIZE, DEFAULT_COLOR
from model.image_bounding_boxes import ImageBoundingBoxes


def rgb_to_bgr(rgb: tuple[int, int, int]) -> tuple:
    """
    Convert RGB to BGR.

    Args:
        rgb (tuple[int, int, int]): RGB color tuple.
    Returns:
        tuple: BGR color tuple.
    """
    return rgb[::-1]


def get_rgb_color(class_number: int, rgb_colors: dict[int, tuple[int, int, int]] = None) -> tuple[int, int, int]:
    """
    Get RGB color.

    Args:
        class_number (int): Class number.
        rgb_colors (dict[int, tuple[int, int, int]], optional): Dictionary mapping class numbers to RGB colors.
    Returns:
        tuple[int, int, int]: RGB color tuple for the class number.
    """
    return rgb_colors[class_number] if rgb_colors is not None and class_number in rgb_colors else DEFAULT_COLOR


def get_bgr_color(class_number: int, rgb_colors: dict[int, tuple[int, int, int]] = None)-> tuple:
    """
    Get BGR color.

    Args:
        class_number (int): Class number.
        rgb_colors (dict[int, tuple[int, int, int]], optional): Dictionary mapping class numbers to RGB colors.
    Returns:
        tuple[int, int, int]: BGR color tuple for the class number.
    """
    return rgb_to_bgr(get_rgb_color(class_number, rgb_colors))


def display_detections(model_class_names: dict, preprocessed_image, image_bounding_boxes: ImageBoundingBoxes,
                       draw_labels_name=False, font=cv2.FONT_HERSHEY_SIMPLEX,
                       font_x_diff=0, font_y_diff=-10, font_scale=0.9, thickness=2,
                       rgb_colors: dict[int, tuple[int, int, int]] = None):
    """
    Function to display the preprocessed image and the image with detections.
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
            class_name = model_class_names[class_number]
            color = get_rgb_color(class_number, rgb_colors)
            cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(image_with_detections, class_name, (x1 + font_x_diff, y1 + font_y_diff), font, font_scale,
                        color, thickness)

    else:
        for i in range(n):
            x1, y1, x2, y2 = xyxy[i].astype(int)
            class_number = int(class_numbers[i])
            color = get_rgb_color(class_number, rgb_colors)
            cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(image_with_detections, str(class_number), (x1 + font_x_diff, y1 + font_y_diff), font,
                        font_scale, color,
                        thickness)

    # Convert the image back to HWC format
    plt.subplot(1, 2, 2)
    plt.imshow(image_with_detections)
    plt.title('Image with Detections')
    plt.show()


def preprocess(image_path, image_size: tuple[int, int] = DEFAULT_SIZE)-> tuple:
    """
    Preprocess the image.

    Args:
        image_path (str): Path to the image file.
        image_size (tuple[int, int]): Size to resize the image to, default is DEFAULT_SIZE.
    Returns:
        tuple: Original image and preprocessed image tensor.
    """
    # Resize the image and convert it to RGB
    image = cv2.imread(image_path)
    image_resized = cv2.resize(image, image_size)
    image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)

    # Normalize the image and transpose it
    image_normalized = image_rgb.astype(np.float32) / 255.0
    image_transposed = np.transpose(image_normalized, (2, 0, 1))

    # Expand the dimensions
    image_expanded = np.expand_dims(image_transposed, axis=0)
    return image, image_expanded
