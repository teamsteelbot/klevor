from opencv.image_augmentation import augment_dataset
from yolo.constants import YOLO_DATASET_LABELED_PROCESSED, YOLO_DATASET_LABELED_TO_PROCESS, YOLO_DATASET_AUGMENTED_TO_PROCESS

# Number of augmentations
NUM_AUGMENTATIONS = 10

if __name__ == '__main__':
    # Augment the dataset
    augment_dataset(YOLO_DATASET_LABELED_TO_PROCESS, YOLO_DATASET_AUGMENTED_TO_PROCESS, NUM_AUGMENTATIONS, YOLO_DATASET_LABELED_PROCESSED)
