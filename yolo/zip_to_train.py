import os
import zipfile
from files.zip import zip_nested_folder, zip_not_nested_folder


# Define the function to zip the required files for model training
def zip_to_train(input_dir: str, input_yolo_dir:str, input_yolo_dataset_organized_to_process_dir: str, output_zip_dir: str,
                 model_name: str):
    # Define the output zip filename
    output_zip_filename = model_name+'_to_train.zip'
    output_zip_path = os.path.join(output_zip_dir, output_zip_filename)

    with (zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf):
        # Zip the folders except the YOLO folder
        zip_nested_folder(zipf, input_dir, input_dir, ['yolo', '.git','.venv', '.idea'])
        print('Zip the folders except the YOLO folder')

        # Zip the YOLO folder files except the dataset, runs and zip folders
        zip_not_nested_folder(zipf, input_dir, input_yolo_dir)
        print('Zip the YOLO folder files except the dataset, runs and zip folders')

        # Zip the YOLO dataset organized files
        zip_nested_folder(zipf, input_dir, input_yolo_dataset_organized_to_process_dir)
        print('Zip the YOLO dataset organized files')
