import os
import zipfile
from files.zip import zip_nested_folder, zip_not_nested_folder

# Define the function to zip the required files for model training
def zip_to_train(input_yolo_dir: str, input_yolo_dataset_organized_to_process_dir: str, output_zip_dir: str,
                 model_name: str,
                 ignore_dirs: list[str] = None, ignore_filenames_regex: list[str] = None):
    # Define the output zip filename
    output_zip_filename = model_name+'_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the YOLO files
        zip_not_nested_folder(zipf, input_yolo_dir, input_yolo_dir)

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_yolo_dir, input_yolo_dataset_organized_to_process_dir, ignore_dirs,
                          ignore_filenames_regex)
