from yolo.constants import YOLO_EPOCHS
from yolo.load import load_pt_model

# Train model
def train_model(yolo_path='yolo11n.pt', device='cpu', data='data.yaml', epochs=YOLO_EPOCHS, imgsz=640, project='yolo',
                name='model'):
    # Load a model
    model = load_pt_model(yolo_path)

    # Train the model
    model.train(
        data=data,
        epochs=epochs,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
    )
