from yolo.constants import YOLO_RUNS_2C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, YOLO_2C_COLORS
from yolo.load import load_pt_model, get_pt_model_class_names
from yolo.test_random import test_random_images
from opencv.model_inference import run_pt_inference

if __name__ == '__main__':
    model = load_pt_model(YOLO_RUNS_2C_WEIGHTS_BEST_PT)
    model_class_names = get_pt_model_class_names(model)
    test_random_images(model, model_class_names, run_pt_inference, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS, False, YOLO_2C_COLORS)

