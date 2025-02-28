from yolo.constants import YOLO_DATASET_LABELED_4C, YOLO_DATASET_LABELED_2C
from yolo.transform import filter_classes
import os

# JSON filename
JSON_FILENAME = 'initial_training.json'

# Classes included in the dataset with 2 classes
INCLUDED_CLASSES = ['red rectangular prism', 'green rectangular prism']

if __name__ == '__main__':
    # Set the input and output path
    input_file_path = os.path.join(YOLO_DATASET_LABELED_4C, JSON_FILENAME)
    output_file_path = os.path.join(YOLO_DATASET_LABELED_2C, JSON_FILENAME)

    # Filter the classes
    filter_classes(input_file_path, output_file_path, INCLUDED_CLASSES)
