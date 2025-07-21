import os
from multiprocessing import Queue
from multiprocessing.synchronize import Event as EventCls

from .object_detector import ObjectDetector


def object_detector_target(
		debug: bool,
		yolo_version: str,
		model_g_inferences_queue: Queue,
		model_m_inferences_queue: Queue,
		model_r_inferences_queue: Queue,
		start_event: EventCls,
		parking_event: EventCls,
		stop_event: EventCls,
		photographer_images_queue: Queue,
		writer_messages_queue: Queue,
		):
	"""
	Target function for a multiprocessing process that handles the
	ObjectDetector.

	Args:
		debug (bool): Flag to indicate if the object detector is in debug mode.
		yolo_version (str): The version of YOLO to use for object detection.
		model_g_inferences_queue (Queue): Queue to hold inferences for model G.
		model_m_inferences_queue (Queue): Queue to hold inferences for model M.
		model_r_inferences_queue (Queue): Queue to hold inferences for model R.
		start_event (EventCls): Event to signal when the object detector should start.
		parking_event (EventCls): Event to signal the parking state of the robot.
		stop_event (EventCls): Event to signal when the object detector should stop.
		photographer_images_queue (Queue): Queue to hold input images for processing.
		writer_messages_queue (Queue): Queue to hold log messages.
	"""
	print(
		"Initializing ObjectDetector in multiprocessing mode. Process ID: ",
		os.getpid(),
		)

	# Initialize the object detector
	object_detector = ObjectDetector(
		debug=debug,
		yolo_version=yolo_version,
		model_g_inferences_queue=model_g_inferences_queue,
		model_m_inferences_queue=model_m_inferences_queue,
		model_r_inferences_queue=model_r_inferences_queue,
		start_event=start_event,
		parking_event=parking_event,
		stop_event=stop_event,
		photographer_images_queue=photographer_images_queue,
		writer_messages_queue=writer_messages_queue,
		)

	# Run the object detector
	object_detector.run()
