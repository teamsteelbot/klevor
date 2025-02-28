from opencv.constants import DEFAULT_SIZE
from opencv.image_resize import resize_image
from yolo.constants import YOLO_DATASET_ORIGINAL_TO_PROCESS, YOLO_DATASET_RESIZED_TO_PROCESS, \
    YOLO_DATASET_ORIGINAL_PROCESSED

if __name__ == '__main__':
    resize_image(YOLO_DATASET_ORIGINAL_TO_PROCESS, YOLO_DATASET_RESIZED_TO_PROCESS, DEFAULT_SIZE,
                 YOLO_DATASET_ORIGINAL_PROCESSED)
