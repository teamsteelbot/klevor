from yolo.zip_to_train import zip_to_train
from yolo.constants import CWD, YOLO,YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_ZIP, YOLO_2C_NAME

if __name__ == '__main__':
    zip_to_train(CWD,YOLO,YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_ZIP, YOLO_2C_NAME)
