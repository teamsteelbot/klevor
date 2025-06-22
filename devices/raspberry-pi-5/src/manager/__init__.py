from multiprocessing.managers import BaseManager

from ..log import Logger
from ..server import WebsocketsServer
from ..serial_communication import SerialCommunication
from ..rplidar import RPLIDAR
from ..camera import Camera
from ..camera.image_processing_queue import ImageProcessingQueue
from ..yolo.hailo.object_detection import ObjectDetection

class Manager(BaseManager):
    """
    Custom manager class used to manage shared resources across processes.
    """
    pass

# Register shared resources with the manager
Manager.register('logger', Logger)
Manager.register('websockets_server', WebsocketsServer)
Manager.register('serial_communication', SerialCommunication)
Manager.register('rplidar', RPLIDAR)
Manager.register('camera', Camera)
Manager.register('image_processing_queue', ImageProcessingQueue)
Manager.register('object_detection', ObjectDetection)

