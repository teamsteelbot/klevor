from yolo.zip_to_train import zip_to_train
from yolo.constants import YOLO, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_ZIP, YOLO_ZIP_IGNORE_DIRS, YOLO_4C_NAME

if __name__ == '__main__':
    zip_to_train(YOLO, YOLO_DATASET_ORGANIZED_4C_TO_PROCESS, YOLO_ZIP, YOLO_4C_NAME, YOLO_ZIP_IGNORE_DIRS)
