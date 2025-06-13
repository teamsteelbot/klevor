from argparse import ArgumentParser
import os

from yolo.args import Args
from yolo.files import Files


def main() -> None:
    """
    Main function to run the script.
    """
    parser = ArgumentParser(description='Script to move YOLO model runs folder to old runs folder')
    Args.add_yolo_version_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args(args, Args.VERSION)

    # Get the runs folder path
    yolo_runs_dir = Files.get_yolo_runs_dir_path(arg_yolo_version)

    # Get the runs folder path with the new name
    yolo_runs_new_name_dir = Files.get_yolo_runs_new_name_dir_path(arg_yolo_version)

    # Check if the new name folder exists
    if os.path.exists(yolo_runs_new_name_dir):
        print(f'Error: The folder {yolo_runs_new_name_dir} already exists')
        exit(1)

    # Check if the runs folder exists
    if not os.path.exists(yolo_runs_dir):
        print(f"Error: The folder {yolo_runs_dir} doesn't exists")
        exit(1)

    # Rename the folder
    os.rename(yolo_runs_dir, yolo_runs_new_name_dir)

    # Get the old runs folder path
    yolo_old_runs_dir = Files.get_yolo_old_runs_dir_path(arg_yolo_version)

    # Move the folder
    Files.move_folder(yolo_runs_new_name_dir, yolo_old_runs_dir)


if __name__ == '__main__':
    main()
