from argparse import ArgumentParser
from typing import List

import torch

from ..args import Args
from ..files import Files


def update_classes(model_name: str, model_version: str, new_classes: List[str]):
	"""
	Update classes from a PyTorch model.

	Args:
		model_name (str): Name of the YOLO model.
		model_version (str): Version of the YOLO model.
		new_classes (List): List of new class names to update in the model.
	"""
	# Get the model path
	model_path = Files.get_model_best_pt_path(model_name, model_version)

	# Load the model
	model = torch.load(model_path, weights_only=False)

	# Check if the model has the same number of classes as the new classes
	if len(model["model"].names) != len(new_classes):
		print(
			f"Error: The model has {len(model['model'].names)} classes, but the new classes have {len(new_classes)} classes.",
			)
		return

	# Update class names
	model["model"].names = new_classes

	# Save the modified model
	torch.save(model, model_path)


if __name__ == "__main__":
	parser = ArgumentParser(description='Script to update YOLO model classes')
	args = Args(parser)
	args.add_yolo_input_model_argument()
	args.add_yolo_version_argument()
	args.add_yolo_classes_argument()

	# Get the YOLO input model
	arg_yolo_input_model = args.get_yolo_input_model()

	# Get the YOLO version
	arg_yolo_version = args.get_yolo_version()

	# Get the YOLO classes
	arg_yolo_classes = args.get_yolo_classes()

	# Update the classes
	update_classes(arg_yolo_input_model, arg_yolo_version, arg_yolo_classes)
