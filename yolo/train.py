from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("./yolo/yolo11n.pt")

    # Train the model
    train_results = model.train(
        data="./yolo/data.yaml",
        epochs=100,
        imgsz=640,
        device="cpu",
        project="./yolo/runs",
        name="steel-bot"
    )

    # Export the model to ONNX format
    path = model.export(format="onnx")  # return path to exported model