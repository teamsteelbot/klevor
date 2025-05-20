import argparse

from args import parse_args_as_dict, get_attribute_from_args
from yolo import (YOLO_EPOCHS, ARGS_YOLO_DEVICE, ARGS_YOLO_INPUT_MODEL_PT, ARGS_YOLO_EPOCHS, ARGS_YOLO_IMAGE_SIZE,
                ARGS_YOLO_INPUT_MODEL)
from model.yolo import load
from yolo.args import (add_yolo_input_model_argument, add_yolo_input_model_pt_argument, add_yolo_device_argument,
    add_yolo_epochs_argument, add_yolo_image_size_argument)
from yolo.files import get_model_local_data_path


# Train model
def train_model(model='yolo11n.pt', device='cpu', data='data.yaml', epochs=YOLO_EPOCHS, imgsz=640, project='yolo',
                name='model'):
    # Load a model
    model = load(model)

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
    parser = argparse.ArgumentParser(description='Script to train YOLO model')
    add_yolo_input_model_argument(parser)
    add_yolo_input_model_pt_argument(parser)
    add_yolo_epochs_argument(parser)
    add_yolo_device_argument(parser)
    add_yolo_image_size_argument(parser)
    args = parse_args_as_dict(parser)

    # Get the YOLO input model
    arg_yolo_input_model = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL)

    # Get the YOLO input PyTorch model
    arg_yolo_input_model_pt = get_attribute_from_args(args, ARGS_YOLO_INPUT_MODEL_PT)

    # Get the YOLO epochs
    arg_yolo_epochs = get_attribute_from_args(args, ARGS_YOLO_EPOCHS)

    # Get the YOLO device
    arg_yolo_device = get_attribute_from_args(args, ARGS_YOLO_DEVICE)

    # Get the YOLO image size
    arg_yolo_image_size = get_attribute_from_args(args, ARGS_YOLO_IMAGE_SIZE)

    # Get model local data path
    model_local_data_path = get_model_local_data_path(arg_yolo_input_model)

    # Train the model
    train_model(model=arg_yolo_input_model_pt, data=model_local_data_path, epochs=arg_yolo_epochs, imgsz=arg_yolo_image_size, project=arg_yolo_input_model, name=arg_yolo_input_model)
