from yolo.constants import YOLO_RUNS_2C_WEIGHTS_BEST_PT, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS
from opencv.model_testing import load_pt_model, run_pt_inference
from yolo.test_random import test_random_images

if __name__ == '__main__':
    # Load the model
    model = load_pt_model(YOLO_RUNS_2C_WEIGHTS_BEST_PT)

    test_random_images(model, model.names, run_pt_inference, YOLO_DATASET_ORGANIZED_2C_TO_PROCESS)

