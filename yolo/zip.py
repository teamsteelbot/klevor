import os
import zipfile

# Define the function to zip the files in a folder
def zip_files(zipf, filenames, input_file_base_path: str, input_base_path:str, ignore_filenames:list = None):
    for filename in filenames:
        # Skip the file if it is in the ignore list
        if ignore_filenames is not None and filename in ignore_filenames:
            continue

        # Zip the file
        file_path = os.path.join(input_file_base_path, filename)
        file_rel_path = os.path.relpath(file_path, input_base_path)
        zipf.write(file_path, file_rel_path)

        # Log
        print(f'Zipped file: {file_rel_path}')

# Define the function to zip a folder, this ignores nested folders
def zip_not_nested_folder(zipf, input_folder_path:str, input_base_path:str, ignore_filenames:list=None):
    # Get the list of files in the specified folder
    filenames = [f for f in os.listdir(input_folder_path)]

    # Zip the files in the folder
    zip_files(zipf, filenames, input_folder_path, input_base_path, ignore_filenames)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')

# Define the function to zip a folder, this includes nested folders
def zip_nested_folder(zipf, input_base_path:str, input_folder_path:str, ignore_filenames:list=None):
    for root, _, filenames in os.walk(input_folder_path):
        # Zip the files in the subfolders
        zip_files(zipf, filenames, root, input_base_path, ignore_filenames)

        # Log
        input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
        print(f'Zipped folder: {input_folder_rel_path}')

# Define the function to zip the required files for model training
def zip_to_train(input_yolo_dir:str, input_yolo_dataset_organized_to_process_dir:str, output_zip_dir:str, output_zip_filename:str):
    output_zip_path=os.path.join(output_zip_dir, output_zip_filename)

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Zip the YOLO files
        zip_not_nested_folder(zipf, input_yolo_dir, input_yolo_dir, [output_zip_filename])

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_yolo_dir, input_yolo_dataset_organized_to_process_dir)

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo')
    input_yolo_dir = os.path.join(base_dir)
    input_yolo_dataset_organized_to_process_dir = os.path.join(base_dir, 'dataset', 'organized', 'to_process')
    output_zip_dir=base_dir
    output_zip_filename = 'steel_bot_to_train.zip'

    zip_to_train(input_yolo_dir, input_yolo_dataset_organized_to_process_dir, output_zip_dir, output_zip_filename)