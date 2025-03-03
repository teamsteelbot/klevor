from model.model_yolo import quantize, load

# Quantize the model and save it
def quantize_model(input_path:str):
    # Load the model
    model = load(input_path)

    # Quantize the model
    path = quantize(model)

    # Log
    print("Model quantized and saved to", path)