# Custom class that represents the detected objects bounding boxes from a YOLO model on an image
class ImageBoundingBoxes:
    # Constructor
    def __init__(self, boxes):
        # Get the bounding box coordinates
        self.__xywh = boxes.xywh.cpu().numpy()
        self.__xywhn = boxes.xywhn.cpu().numpy()
        self.__xyxy = boxes.xyxy.cpu().numpy()
        self.__xyxyn = boxes.xyxyn.cpu().numpy()
        self.__cls = boxes.cls.cpu().numpy()
        self.__conf = boxes.conf.cpu().numpy()
        self.__n = len(self.__cls)

    # String representation of the objects detected in the image
    def __str__(self):
        bounding_boxes = []
        for i in range(self.__n):
            bounding_box_attributes = [
                f"Class: {int(self.__cls[i])}",
                f"Confidence: {self.__conf[i]}",
                f"(X0, Y0): ({self.__xyxyn[i][0]}, {self.__xyxyn[i][1]})",
                f"(X1, Y1): ({self.__xyxyn[i][2]}, {self.__xyxyn[i][3]})",
            ]
            bounding_boxes.append(f"Box {i + 1}:\n\t" + "\n\t".join(bounding_box_attributes))
        return "\n".join(bounding_boxes)

    # Get the number of detected objects
    def get_number_of_objects(self):
        return self.__n

    # Get the bounding box coordinates in the format (x1, y1, x2, y2)
    def get_xyxy(self):
        return self.__xyxy

    # Get the bounding box coordinates in the format (x_center, y_center, width, height)
    def get_xywh(self):
        return self.__xywh

    # Get the bounding box coordinates in the format (x_center, y_center, width, height) normalized
    def get_xywhn(self):
        return self.__xywhn

    # Get the bounding box coordinates in the format (x1, y1, x2, y2) normalized
    def get_xyxyn(self):
        return self.__xyxyn

    # Get the classes of the detected objects
    def get_classes(self):
        return self.__cls

    # Get the confidence of the detected objects
    def get_confidences(self):
        return self.__conf

    # Get the bounding box coordinates and class of the detected objects
    def get_boxes(self):
        return self.__cls, self.__conf, self.__xyxy


# Convert the outputs to image bounding boxes instance
def outputs_to_image_bounding_boxes(outputs):
    return ImageBoundingBoxes(outputs[0].boxes)
