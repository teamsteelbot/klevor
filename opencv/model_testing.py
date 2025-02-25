from ultralytics import YOLO
import cv2
import numpy as np
import time
import torch
from opencv.constants import DEFAULT_SIZE
import matplotlib.pyplot as plt
from opencv.model_types import ImageBoundingBoxes

# Function to display the preprocessed image and the image with detections
def display_detections(preprocessed_image, outputs):
    # Convert the image back to HWC format
    preprocessed_image_hwc = np.transpose(preprocessed_image[0], (1, 2, 0))
    plt.subplot(1, 2, 1)
    plt.imshow(preprocessed_image_hwc)
    plt.title('Preprocessed Image')

    # Convert the image back to HWC format
    plt.subplot(1, 2, 2)
    plt.imshow(outputs[0].plot())
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