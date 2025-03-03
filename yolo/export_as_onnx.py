from model.model_yolo import load, export_onnx

# Export the model to ONNX format
def export_model(model_path):
    # Load a model
    model = load(model_path)

    # Export the model
    path = export_onnx(model)

    # Log
    print(f"Model exported to {path}")