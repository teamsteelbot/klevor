from yolo.constants import YOLO_RUNS_4C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_4C_COLORS
from yolo.test import test_random_images_pt

if __name__ == '__main__':
    test_random_images_pt(YOLO_RUNS_4C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_4C_COLORS)