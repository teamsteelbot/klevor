from ultralytics import YOLO


# Train model
def train_model(yolo_path='yolo11n.pt', device='cpu', data='data.yaml', epochs=100, imgsz=640, project='yolo',
                name='model'):
    # Load a model
    model = YOLO(yolo_path)

    # Train the model
    train_results = model.train(
        data=data,
        epochs=epochs,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
    )

    # Export the model to ONNX format
    path = model.export(format="onnx")

    # Log
    print(f"Model exported to {path}")
