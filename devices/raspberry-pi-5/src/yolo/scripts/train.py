import os
from argparse import ArgumentParser

from .. import Yolo
from ..args import Args, Flag
from ..constants import EPOCHS
from ..files import Files
from ...constants import SIZE


def train_model(model: str = 'yolo11n.pt', device: str = 'cpu',
                data: str | os.PathLike[str] = 'data.yaml',
                epochs: int = EPOCHS, imgsz: int = SIZE, project: str = 'yolo',
                name: str = 'model') -> None:
    """
    Train model.

    Args:
        model (str): Path to the YOLO model file.
        device (str): Device to use for training (e.g., 'cpu', 'cuda').
        data (str | os.PathLike[str]): Path to the dataset configuration file.
        epochs (int): Number of training epochs.
        imgsz (int): Image size for training.
        project (str): Project name for saving results.
        name (str): Name of the model.
    """
    # Load a model
    model = Yolo.load(model)

    # Train the model
    model.train(
        data=data,
        epochs=epochs,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
    )


if __name__ == '__main__':
    parser = ArgumentParser(description='Script to train YOLO model')
    Args.add_yolo_input_model_argument(parser)
    Args.add_yolo_input_model_pt_argument(parser)
    Args.add_yolo_epochs_argument(parser)
    Args.add_yolo_device_argument(parser)
    Args.add_yolo_image_size_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = Args.get_attribute_from_args_dict(args,
                                                             Flag.INPUT_MODEL)

    # Get the YOLO input PyTorch model
    arg_yolo_input_model_pt = Args.get_attribute_from_args_dict(args,
                                                                Flag.INPUT_MODEL_PT)

    # Get the YOLO epochs
    arg_yolo_epochs = Args.get_attribute_from_args_dict(args, Flag.EPOCHS)

    # Get the YOLO device
    arg_yolo_device = Args.get_attribute_from_args_dict(args, Flag.DEVICE)

    # Get the YOLO image size
    arg_yolo_image_size = Args.get_attribute_from_args_dict(args,
                                                            Flag.IMAGE_SIZE)

    # Get model local data path
    model_local_data_path = Files.get_model_local_data_path(
        arg_yolo_input_model)

    # Train the model
    train_model(model=arg_yolo_input_model_pt, data=model_local_data_path,
                epochs=arg_yolo_epochs,
                imgsz=arg_yolo_image_size, project=arg_yolo_input_model,
                name=arg_yolo_input_model,
                device=arg_yolo_device)
