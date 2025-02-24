from ultralytics import YOLO

# Load a model
model = YOLO('yolov11.yaml')

if __name__ == '__main__':
    # Train the model
    model.train(data='data.yaml', epochs=100, imgsz=640)