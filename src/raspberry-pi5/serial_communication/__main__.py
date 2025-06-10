from serial import Serial

if __name__ == "__main__":
    # Create an instance of SerialCommunication
    serial = Serial(
        port="/dev/ttyUSB0",  # Replace with your actual serial port
        baudrate=115200,      # Replace with your actual baud rate
        timeout=1             # Optional timeout for read operations
    )
    # Check the type of serial communication
    check_type(serial_communication, SerialCommunication)

    # Get the stop event
    stop_event = serial_communication.get_stop_event()

    # Thread to handle receiving messages
    thread_1 = Thread(target=serial_communication.receive_message, args=(stop_event, serial_communication))
    thread_1.start()
    thread_1.join()

    # Thread to handle sending messages
    thread_2 = Thread(target=serial_communication.send_message, args=(stop_event, serial_communication))
    thread_2.start()
    thread_2.join()
