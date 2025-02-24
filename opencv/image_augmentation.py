import cv2
import albumentations as A
import os
import time

# Augment labeled images
def augment_images(image_path, annotations_path, output_image_dir, output_annotations_dir, num_augmentations=5):
    # Get current time
    start_time = time.time()

    # Read the image and convert it to RGB
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Read the annotations
    with open(annotations_path, 'r') as f:
        lines = f.readlines()

    # Parse the annotations
    bboxes = []
    class_labels = []
    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center, y_center, width, height = map(float, parts[1:])
        bboxes.append([x_center, y_center, width, height])
        class_labels.append(class_id)

    # Define the augmented pipeline
    transform = A.Compose([
        # Apply with a 50% probability a random brightness and contrast adjustment
        A.RandomBrightnessContrast(p=0.5),

        # Apply with a 50% probability a horizontal flip
        A.HorizontalFlip(p=0.5),

        # Apply with a 50% probability a random shift, scale, and rotation
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),

        # Apply with a 30% probability a random RGB shift
        A.RGBShift(r_shift_limit=25, g_shift_limit=25, b_shift_limit=25, p=0.3),

        # Apply with a 30% probability a random crop
        A.RandomCrop(width=int(image.shape[1] * 0.9), height=int(image.shape[0] * 0.9), p=0.3), #Optional random crop
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

    # Apply the augmented pipeline to the image and annotations
    try:
        for i in range(num_augmentations):
            transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            transformed_image = transformed['image']
            transformed_bboxes = transformed['bboxes']
            transformed_class_labels = transformed['class_labels']

            # Save the augmented image and annotations
            output_image_path = os.path.join(output_image_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_aug_{i}.jpg")
            output_annotations_path = os.path.join(output_annotations_dir, f"{os.path.splitext(os.path.basename(annotations_path))[0]}_aug_{i}.txt")

            # Convert the image back to BGR and save it
            cv2.imwrite(output_image_path, cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))

            # Log the image
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Augmented image saved to {output_image_path} in {elapsed_time:.2f} seconds")

            # Save the annotations
            with open(output_annotations_path, 'w') as f:
                for j, bbox in enumerate(transformed_bboxes):
                    class_id = transformed_class_labels[j]
                    x_center, y_center, width, height = bbox
                    f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

            # Log annotations
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Augmented annotations saved to {output_annotations_path} in {elapsed_time:.2f} seconds")
    except Exception as e:
        print(f"Error: {e} for {image_path}")

# Augment a dataset
def augment_dataset(image_dir, annotations_dir, output_image_dir, output_annotations_dir, num_augmentations=5):
    # Check if the output directories exist, if not it creates them
    for output_dir in [output_image_dir, output_annotations_dir]:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # Get the image files
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Augment each image
    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        annotations_file = os.path.splitext(image_file)[0] + '.txt'
        annotations_path = os.path.join(annotations_dir, annotations_file)

        if os.path.exists(annotations_path):
            augment_images(image_path, annotations_path, output_image_dir, output_annotations_dir, num_augmentations)
        else:
            print(f"Warning: Annotation file not found for {image_file}")
