from yolo.quantize import quantize_model
from yolo.constants import YOLO_RUNS_4C_WEIGHTS_BEST_PT

if __name__ == '__main__':
    quantize_model(YOLO_RUNS_4C_WEIGHTS_BEST_PT)