import os
import zipfile

# Define the function to zip the files in a folder
def zip_files(zipf, files, input_file_base_path: str, input_base_path:str):
    for file in files:
        # Zip the file
        file_path = os.path.join(input_file_base_path, file)
        file_rel_path = os.path.relpath(file_path, input_base_path)
        zipf.write(file_path, file_rel_path)

        # Log
        print(f'Zipped file: {file_rel_path}')

# Define the function to zip a folder, this ignores nested folders
def zip_not_nested_folder(zipf, input_folder_path:str, input_base_path:str):
    # Get the list of files in the specified folder
    files = [f for f in os.listdir(input_folder_path)]

    # Zip the files in the folder
    zip_files(zipf, files, input_folder_path, input_base_path)

    # Log
    input_folder_rel_path = os.path.relpath(input_folder_path, input_base_path)
    print(f'Zipped folder: {input_folder_rel_path}')

# Define the function to zip a folder, this includes nested folders
def zip_nested_folder(zipf, input_base_path:str, input_folder_path:str):
    for root, dirs, files in os.walk(input_folder_path):
        # Zip the files in the subfolders
        zip_files(zipf, files, root, input_base_path)

        # Log
        print(f'Zipped folder: {root} from {input_base_path}')

# Define the function to zip the required files for model training
def zip_to_train(input_yolo_dir:str, input_yolo_dataset_organized_to_process_dir:str, output_zip:str):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Zip the YOLO files
        zip_not_nested_folder(zipf, input_yolo_dir, input_yolo_dir)

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_yolo_dir, input_yolo_dataset_organized_to_process_dir)

if __name__ == '__main__':
    # Set the input and output directories
    cwd = os.getcwd()
    base_dir = os.path.join(cwd, 'yolo')
    input_yolo_dir = os.path.join(base_dir)
    input_yolo_dataset_organized_to_process_dir = os.path.join(base_dir, 'dataset', 'organized', 'to_process')
    output_zip = os.path.join(base_dir, 'steel_bot_to_train.zip')

    zip_to_train(input_yolo_dir, input_yolo_dataset_organized_to_process_dir, output_zip)