from yolo.export_as_onnx import export_model
from yolo.constants import YOLO_RUNS_4C_WEIGHTS_BEST_PT

if __name__ == '__main__':
    export_model(YOLO_RUNS_4C_WEIGHTS_BEST_PT)