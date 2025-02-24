import os
import opencv.image_augmentation as ia

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'data')
    labeled_dir = os.path.join(base_dir, 'labeled')
    augmented_dir = os.path.join(base_dir, 'augmented')

    input_to_processed_dir = os.path.join(labeled_dir, 'to_process')
    output_augmented_dir = os.path.join(augmented_dir, 'to_process')
    output_processed_dir = os.path.join(labeled_dir, 'processed')
    num_augmentations = 10

    ia.augment_dataset(input_to_processed_dir, output_augmented_dir, num_augmentations, output_processed_dir)
