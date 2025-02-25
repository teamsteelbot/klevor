import os
import zipfile
from files.zip import zip_nested_folder, zip_not_nested_folder

# Define the function to zip the required files for model training
def zip_to_train(input_yolo_dir:str, input_yolo_dataset_organized_to_process_dir:str, output_zip_dir:str, output_zip_filename:str,
                 ignore_dirs:list[str]=None, ignore_filenames:list[str]=None):
    output_zip_path=os.path.join(output_zip_dir, output_zip_filename)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the YOLO files
        not_nested_folder_ignore_filenames=[output_zip_filename]
        if ignore_filenames is not None:
            not_nested_folder_ignore_filenames += [f for f in ignore_filenames if f != output_zip_filename]
        zip_not_nested_folder(zipf, input_yolo_dir, input_yolo_dir, not_nested_folder_ignore_filenames)

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_yolo_dir, input_yolo_dataset_organized_to_process_dir, ignore_dirs, ignore_filenames)

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo')
    input_yolo_dir = os.path.join(base_dir)
    input_yolo_dataset_organized_to_process_dir = os.path.join(base_dir, 'dataset', 'organized', 'to_process')
    output_zip_dir=base_dir
    output_zip_filename = 'steel_bot_to_train.zip'
    ignore_dirs = ['runs']
    ignore_filenames = ['runs-20250225T125604Z-001.zip']

    zip_to_train(input_yolo_dir, input_yolo_dataset_organized_to_process_dir, output_zip_dir, output_zip_filename, ignore_dirs, ignore_filenames)