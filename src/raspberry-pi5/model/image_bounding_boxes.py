class ImageBoundingBoxes:
    """
    Custom class that represents the detected objects bounding boxes from a YOLO model on an image.
    """

    def __init__(self, boxes):
        """
        Constructor.
        """
        # Get the bounding box coordinates
        self.__xywh = boxes.xywh.cpu().numpy()
        self.__xywhn = boxes.xywhn.cpu().numpy()
        self.__xyxy = boxes.xyxy.cpu().numpy()
        self.__xyxyn = boxes.xyxyn.cpu().numpy()
        self.__cls = boxes.cls.cpu().numpy()
        self.__conf = boxes.conf.cpu().numpy()
        self.__n = len(self.__cls)

    def __str__(self):
        """
        String representation of the objects detected in the image.
        """
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

    def get_number_of_objects(self):
        """
        Get the number of detected objects.
        """
        return self.__n

    def get_xyxy(self):
        """
        Get the bounding box coordinates in the format (x1, y1, x2, y2).
        """
        return self.__xyxy

    def get_xywh(self):
        """
        Get the bounding box coordinates in the format (x_center, y_center, width, height).
        """
        return self.__xywh

    def get_xywhn(self):
        """
        Get the bounding box coordinates in the format (x_center, y_center, width, height) normalized.
        """
        return self.__xywhn

    def get_xyxyn(self):
        """
        Get the bounding box coordinates in the format (x1, y1, x2, y2) normalized.
        """
        return self.__xyxyn

    def get_classes(self):
        """
        Get the classes of the detected objects.
        """
        return self.__cls

    def get_confidences(self):
        """
        Get the confidence of the detected objects.
        """
        return self.__conf

    def get_boxes(self):
        """
        Get the bounding box coordinates and class of the detected objects.
        """
        return self.__cls, self.__conf, self.__xyxy


def outputs_to_image_bounding_boxes(outputs):
    """
    Convert the outputs to image bounding boxes instance.
    """
    return ImageBoundingBoxes(outputs[0].boxes)
