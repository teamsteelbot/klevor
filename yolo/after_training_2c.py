from yolo.constants import YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_PROCESSED
from yolo.after_training import move_folder

if __name__ == '__main__':
    move_folder(YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_DATASET_ORGANIZED_2C_PROCESSED)
