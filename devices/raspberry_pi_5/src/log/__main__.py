from argparse import ArgumentParser
from multiprocessing import Event, Process, Queue
from time import sleep

from . import Logger
from ..args import Args
from .multiprocessing import writer_target

if __name__ == "__main__":
	parser = ArgumentParser(
		description="Script to test the Writer.",
		)
	args = Args(parser)
	args.add_debug_argument()

	# Get the debug mode
	arg_debug = args.get_debug()

	# Create the required queues and events
	writer_messages_queue = Queue()
	stop_event = Event()

	# Create a process for the writer
	writer_process = Process(
		target=writer_target, args=(
			arg_debug, writer_messages_queue, stop_event,
			),
		)
	writer_process.start()

	# Create an instance of Logger
	logger = Logger(writer_messages_queue, debug=arg_debug)

	try:
		# Log a message using the logger
		logger.info("This is a test log message.")

		# Wait for a while to ensure the log messages are processed
		print("Writer is running. Press Ctrl+C to stop.")
		while True:
			# Keep the main thread alive to allow the writer to process messages
			logger.info("Writer is still running...")
			sleep(1)

	except KeyboardInterrupt:
		# Handle keyboard interrupt to stop the writer process gracefully
		print("KeyboardInterrupt received. Stopping writer process...")
		logger.warning("KeyboardInterrupt received. Stopping writer process.")

	except Exception as e:
		# Log any exceptions that occur
		logger.error(f"An error occurred: {e}")

	finally:
		# Stop the writer process and clean up
		stop_event.set()
		writer_process.join()
