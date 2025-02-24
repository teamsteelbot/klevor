import os
import opencv.image_augmentation as ia

if __name__ == '__main__':
    # Set the input and output directories'
    cwd = os.getcwd()
    image_dir = os.path.join(cwd, 'training', 'images', 'labeled', 'images')
    annotations_dir = os.path.join(cwd, 'training','images',  'labeled', 'labels')
    output_image_dir = os.path.join(cwd, 'training', 'images', 'augmented', 'images')
    output_annotations_dir = os.path.join(cwd, 'training', 'images', 'augmented', 'labels')
    ia.augment_dataset(image_dir, annotations_dir, output_image_dir, output_annotations_dir, num_augmentations=10)