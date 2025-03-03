from yolo.constants import YOLO_RUNS_2C_WEIGHTS_BEST_QUANTIZED_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_2C_COLORS
from yolo.test import test_random_images_pt

if __name__ == '__main__':
    test_random_images_pt(YOLO_RUNS_2C_WEIGHTS_BEST_QUANTIZED_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_2C_COLORS)