from multiprocessing import Event

import serial
import time

from camera.images_queue import ImagesQueue


class SerialCommunication:
    """
    Class to handle the serial communication with the Raspberry Pi Pico.
    """
    __stop_event = None
    __images_queue = None

    def __init__(self, images_queue: ImagesQueue):
        """
        Initialize the serial communication class.
        """
        # Check if the images_queue is None
        if not isinstance(images_queue, ImagesQueue):
            raise ValueError("images_queue must be an instance of ImagesQueue")
        self.__images_queue = images_queue

        # Create the stop event
        self.__stop_event = Event()

        # Get the capture image event
        self.__capture_image_event = self.__images_queue.get_capture_image_event()

        print("Serial communication initialized.")

    def stop(self):
        """
        Stop the communication.
        """
        self.__stop_event.set()
        print("Stopping serial communication...")

    def get_stop_event(self):
        """
        Get the stop event status.
        """
        return self.__stop_event

    def __del__(self):
        """
        Destructor for the serial communication.
        """
        # Stop event
        self.stop()

"""
try:
    ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace with your Pico's serial port
    print("Serial port opened successfully!")

    while True:
        message_to_send = "Hello from Pi!\n"
        ser.write(message_to_send.encode('utf-8'))
        print(f"Sent to Pico: {message_to_send.strip()}")
        time.sleep(1)

        if ser.in_waiting > 0:
            received_data = ser.readline().decode('utf-8').strip()
            print(f"Received from Pico: {received_data}")

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
"""

def main(serial_communication: SerialCommunication) -> None:
    """
    Main function to run the script.
    """
    # Check if the serial_communication is None
    if isinstance(serial_communication, SerialCommunication):
        raise ValueError("serial_communication must be an instance of SerialCommunication")

    # Get the stop event
    stop_event = serial_communication.get_stop_event()

    # Wait for the stop event
    stop_event.wait()

if __name__ == "__main__":
    main()