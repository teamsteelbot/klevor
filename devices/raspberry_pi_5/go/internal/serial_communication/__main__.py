from multiprocessing import Event, Process, Queue, Value
from time import sleep
from argparse import ArgumentParser

from ..args import Args
from ..enums import Challenge
from .multiprocessing import serial_communication_target
from ..log import Logger
from ..log.multiprocessing import writer_target

if __name__ == "__main__":
	parser = ArgumentParser(
		description="Script to test the Serial Communication.",
		)
	args = Args(parser)
	args.add_debug_argument()

	# Get the debug mode
	arg_debug = args.get_debug()

	# Create the required queues and events
	writer_messages_queue = Queue()
	writer_stop_event = Event()
	serial_incoming_messages_queue = Queue()
	sender_messages_queue = Queue()
	bno08x_yaw_deg = Value("f", 0)
	bno08x_turns = Value("f", 0)
	start_event = Event()
	stop_event = Event()
	challenge = Value('c', Challenge.NONE.as_char)

	# Create a process for the writer
	writer_process = Process(
		target=writer_target, args=(
			arg_debug, writer_messages_queue, writer_stop_event,
			),
		)
	writer_process.start()

	# Create an instance of Logger
	logger = Logger(writer_messages_queue)

	# Create a process for the serial communication
	serial_communication_process = Process(
		target=serial_communication_target,
		args=(
			arg_debug, challenge, start_event, stop_event, bno08x_yaw_deg,
			bno08x_turns, serial_incoming_messages_queue,
			sender_messages_queue, writer_messages_queue,
			),
		)
	serial_communication_process.start()

	try:
		# Wait indefinitely to keep the serial communication running
		print("SerialCommunication is running. Press Ctrl+C to stop.")
		while True:
			sleep(1)  # Sleep to prevent busy-waiting

	except KeyboardInterrupt:
		# Handle keyboard interrupt to stop the processes gracefully
		print(
			"KeyboardInterrupt received. Stopping serial communication and writer processes...",
			)
		logger.warning(
			"KeyboardInterrupt received. Stopping serial communication and writer processes...",
			)

	except Exception as e:
		# Log any exceptions that occur
		logger.error(f"An error occurred: {e}")

	finally:
		# Stop the serial communication and writer process and clean up
		stop_event.set()
		serial_communication_process.join()
		writer_stop_event.set()
		writer_process.join()
