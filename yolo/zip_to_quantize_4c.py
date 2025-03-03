from yolo.zip_to_quantize import zip_to_quantize
from yolo.constants import CWD, YOLO,YOLO_RUNS, YOLO_ZIP, YOLO_4C_NAME

if __name__ == '__main__':
    zip_to_quantize(CWD,YOLO,YOLO_RUNS, YOLO_ZIP, YOLO_4C_NAME)
