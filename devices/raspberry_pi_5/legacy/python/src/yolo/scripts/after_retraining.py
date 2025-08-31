import os
from argparse import ArgumentParser

from ..args import Args
from ..files import Files

if __name__ == '__main__':
	parser = ArgumentParser(
		description='Script to move YOLO model runs folder to old runs folder',
		)
	args = Args(parser)
	args.add_yolo_version_argument()

	# Get the YOLO version
	arg_yolo_version = args.get_yolo_version()

	# Get the runs folder path
	yolo_runs_dir = Files.get_yolo_runs_dir_path(arg_yolo_version)

	# Get the runs folder path with the new name
	yolo_runs_new_name_dir = Files.get_yolo_runs_new_name_dir_path(
		arg_yolo_version,
		)

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
