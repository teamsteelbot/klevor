from ultralytics import YOLO
import cv2
import numpy as np
import time
import torch
from opencv.constants import DEFAULT_SIZE
import matplotlib.pyplot as plt
from opencv.model_types import ImageBoundingBoxes

# Constants
DEFAULT_COLOR = (0, 255, 0)

# Convert RGB to BGR
def rgb_to_bgr(rgb:tuple[int, int, int]):
    return rgb[::-1]

# Get RGB color
def get_rgb_color(class_number:int, rgb_colors:dict[int, tuple[int, int, int]]=None):
    return rgb_colors[class_number] if rgb_colors is not None and class_number in rgb_colors else DEFAULT_COLOR

# Get BGR color
def get_bgr_color(class_number:int, rgb_colors:dict[int, tuple[int, int, int]]=None):
    return rgb_to_bgr(get_rgb_color(class_number, rgb_colors))

# Function to display the preprocessed image and the image with detections
def display_detections(model, preprocessed_image, outputs, draw_labels_name=False, font=cv2.FONT_HERSHEY_SIMPLEX, font_x_diff=0, font_y_diff=-10, font_scale=0.9, thickness=2, rgb_colors:dict[int, tuple[int, int, int]]=None):
    # Convert the image back to HWC format
    preprocessed_image_hwc = np.transpose(preprocessed_image[0], (1, 2, 0))

    # Convert the image to uint8
    preprocessed_image_uint8 = (preprocessed_image_hwc*255).astype(np.uint8)

    # Display the preprocessed image
    plt.subplot(1, 2, 1)
    plt.imshow(preprocessed_image_uint8)
    plt.title('Preprocessed Image')

    # Get the image with detections
    image_with_detections = preprocessed_image_uint8.copy()

    # Draw bounding boxes with class numbers
    xyxy = outputs[0].boxes.xyxy.cpu().numpy()
    class_numbers = outputs[0].boxes.cls.cpu().numpy()
    n = len(outputs[0].boxes)

    if draw_labels_name is True:
        for i in range(n):
            x1, y1, x2, y2 =  xyxy[i].astype(int)
            class_number = int(class_numbers[i])
            class_name = model.names[class_number]
            color = get_rgb_color(class_number, rgb_colors)
            cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(image_with_detections, class_name, (x1 + font_x_diff, y1 + font_y_diff), font, font_scale, color, thickness)

    else:
        for i in range(n):
            x1, y1, x2, y2 = xyxy[i].astype(int)
            class_number = int(class_numbers[i])
            color = get_rgb_color(class_number, rgb_colors)
            cv2.rectangle(image_with_detections, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(image_with_detections, str(class_number), (x1 + font_x_diff, y1 + font_y_diff), font, font_scale, color,
                        thickness)

    # Convert the image back to HWC format
    plt.subplot(1, 2, 2)
    plt.imshow(image_with_detections)
    plt.title('Image with Detections')
    plt.show()

# Preprocess the image
def preprocess(image_path, image_size:tuple[int, int]=DEFAULT_SIZE):
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

# Load model
def load_model(model_path:str):
    # Load the model
    model = YOLO(model_path)
    model.eval()
    return model

# Run inference
def run_inference(model, preprocessed_image):
    # Get time
    start_time = time.time()

    # Run inference
    outputs = model(torch.from_numpy(preprocessed_image).float())

    # Get time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Log
    print(f'Inference took {elapsed_time:.2f} seconds')

    return outputs

# Convert the outputs to image bounding boxes instance
def outputs_to_image_bounding_boxes(outputs):
    return ImageBoundingBoxes(outputs[0].boxes)