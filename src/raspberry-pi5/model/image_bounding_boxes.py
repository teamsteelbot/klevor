class ImageBoundingBoxes:
    """
    Custom class that represents the detected objects bounding boxes from a YOLO model on an image.
    """

    def __init__(self, xwyhn=None, xyxy=None, xywh=None, xyxyn=None, cls=None, conf=None, n=None):
        """
        Initialize the ImageBoundingBoxes instance with bounding box coordinates, classes, and confidences.
        """
        self.__xywh = xywh
        self.__xywhn = xwyhn
        self.__xyxy = xyxy
        self.__xyxyn = xyxyn
        self.__cls = cls
        self.__conf = conf
        self.__n = n

    def __str__(self) -> str:
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

    @staticmethod
    def from_pt_cpu_boxes(boxes):
        """
        Initialize a new ImageBoundingBoxes instances from a PyTorch CPU tensor.

        Args:
            boxes (torch.Tensor): The bounding boxes' tensor.

        Returns:
            ImageBoundingBoxes: An instance containing the bounding boxes, classes, and confidences.
        """
        return ImageBoundingBoxes(
            xywh=boxes.xywh.cpu().numpy(),
            xywhn=boxes.xywhn.cpu().numpy(),
            xyxy=boxes.xyxy.cpu().numpy(),
            xyxyn=boxes.xyxyn.cpu().numpy(),
            cls=boxes.cls.cpu().numpy(),
            conf=boxes.conf.cpu().numpy(),
            n=len(boxes.cls)
        )

    @staticmethod
    def from_pt_cpu(input_data: list):
        """
        Extract detections from the input data.

        Args:
            input_data (list): Raw detections from the model.

        Returns:
            ImageBoundingBoxes: An instance containing the bounding boxes, classes, and confidences.
        """
        return ImageBoundingBoxes.from_pt_cpu_boxes(input_data[0].boxes)

    @staticmethod
    def from_hailo(input_data: list, threshold: float = 0.5):
        """
        Extract detections from the input data.

        Args:
            input_data (list): Raw detections from the model.
            threshold (float): Score threshold for filtering detections. Defaults to 0.5.

        Returns:
            ImageBoundingBoxes: An instance containing the bounding boxes, classes, and confidences.
        """
        boxes, scores, classes = [], [], []
        num_detections = 0

        for i, detection in enumerate(input_data):
            if len(detection) == 0:
                continue

            for det in detection:
                bbox, score = det[:4], det[4]

                if score >= threshold:
                    boxes.append(bbox)
                    scores.append(score)
                    classes.append(i)
                    num_detections += 1

        return ImageBoundingBoxes(n=num_detections, xyxy=boxes, cls=classes, conf=scores)

    def get_number_of_objects(self):
        """
        Get the number of detected objects.

        Returns:
            int: The number of detected objects.
        """
        return self.__n

    def get_xyxy(self):
        """
        Get the bounding box coordinates in the format (x1, y1, x2, y2).

        Returns:
            list: A list of bounding box coordinates in the format (x1, y1, x2, y2).
        """
        return self.__xyxy

    def get_xywh(self):
        """
        Get the bounding box coordinates in the format (x_center, y_center, width, height).

        Returns:
            list: A list of bounding box coordinates in the format (x_center, y_center, width, height).
        """
        return self.__xywh

    def get_xywhn(self):
        """
        Get the bounding box coordinates in the format (x_center, y_center, width, height) normalized.

        Returns:
            list: A list of bounding box coordinates in the format (x_center, y_center, width, height) normalized.
        """
        return self.__xywhn

    def get_xyxyn(self):
        """
        Get the bounding box coordinates in the format (x1, y1, x2, y2) normalized.

        Returns:
            list: A list of bounding box coordinates in the format (x1, y1, x2, y2) normalized.
        """
        return self.__xyxyn

    def get_classes(self):
        """
        Get the classes of the detected objects.

        Returns:
            list: A list of class indices for each detected object.
        """
        return self.__cls

    def get_confidences(self)-> list:
        """
        Get the confidence of the detected objects.

        Returns:
            list: A list of confidence scores for each detected object.
        """
        return self.__conf

    def get_boxes(self) -> tuple:
        """
        Get the bounding box coordinates and class of the detected objects.

        Returns:
            tuple: A tuple containing the class, confidence, and bounding box coordinates in xyxy format.
        """
        return self.__cls, self.__conf, self.__xyxy