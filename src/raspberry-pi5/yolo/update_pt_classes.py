import torch

from yolo import YOLO_MODEL_3C, YOLO_VERSION_11
from yolo.files import get_model_best_pt_path

# Get the model path
model_path = get_model_best_pt_path(YOLO_MODEL_3C, YOLO_VERSION_11)

# Load the model
model = torch.load(model_path, weights_only=False)

# Update class names
print(model["model"].names)
model["model"].names = ["green rectangular prism", "magenta rectangular prism", "red rectangular prism"]  # Modify as needed

# Save the modified model
torch.save(model, model_path)