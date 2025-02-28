from yolo.load import load_pt_model

# Export the model to ONNX format
def export_model(model_path):
    # Load a model
    model = load_pt_model(model_path)

    # Export the model to ONNX format
    path = model.export(format="onnx")

    # Log
    print(f"Model exported to {path}")