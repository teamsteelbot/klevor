from argparse import ArgumentParser
from multiprocessing import Event, Process, Queue

import matplotlib as plt

from ..opencv import OpenCV
from ..args import Args
from .multiprocessing import photographer_target
from ..log.multiprocessing import writer_target
from ..log import Logger

# Constants
ATTEMPTS = 5

if __name__ == "__main__":
	parser = ArgumentParser(
		description="Script to test the Camera.",
		)
	args = Args(parser)
	args.add_debug_argument()

	# Get the debug mode
	arg_debug = args.get_debug()

	# Create the required queues and events
	writer_messages_queue = Queue()
	images_queue = Queue()
	start_event = Event()
	writer_stop_event = Event()
	stop_event = Event()
	capture_image_event = Event()

	# Create a process for the writer
	writer_process = Process(
		target=writer_target, args=(
			arg_debug, writer_messages_queue, writer_stop_event,
			),
		)
	writer_process.start()

	# Create an instance of Logger
	logger = Logger(writer_messages_queue, debug=arg_debug)

	# Create a process for the photographer
	photographer_process = Process(
		target=photographer_target,
		args=(
			arg_debug, images_queue, capture_image_event, start_event,
			stop_event, writer_messages_queue, OpenCV.preprocess_pil_image,
			),
		)
	photographer_process.start()

	try:
		# Wait indefinitely to keep the photographer running
		print("Photographer is running. Press Ctrl+C to stop.")

		attempts = 0
		while attempts < ATTEMPTS:
			# Simulate capturing an image every second
			capture_image_event.set()
			logger.info("Capturing image...")

			# Wait for the image to be processed
			image = images_queue.get(timeout=5)
			logger.info(f"Image captured: {image}")

			# Visualize the image
			plt.imshow(image)
			plt.title("Image from Photographer")
			plt.axis('off')
			plt.show()

			attempts += 1

	except KeyboardInterrupt:
		# Handle keyboard interrupt to stop the processes gracefully
		print(
			"KeyboardInterrupt received. Stopping camera and writer processes...",
			)
		logger.warning(
			"KeyboardInterrupt received. Stopping camera and writer processes.",
			)

	except Exception as e:
		# Log any exceptions that occur
		logger.error(f"An error occurred: {e}")

	finally:
		# Stop the photographer and writer process and clean up
		stop_event.set()
		photographer_process.join()
		writer_stop_event.set()
		writer_process.join()
