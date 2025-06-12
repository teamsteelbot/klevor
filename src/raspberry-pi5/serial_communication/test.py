import serial
import time

# Configure the serial port
# On Windows, it might be 'COMx' (e.g., 'COM3').
# On macOS, it might be '/dev/cu.usbmodemXXXX'.
# On Linux, it's often '/dev/ttyACM0' or '/dev/ttyUSB0'.
# The baud rate (e.g., 115200) must match the baud rate configured on the receiving device.
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200  # Common baud rate for microcontrollers

try:
    # Open the serial port
    ser = None
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) # timeout helps prevent blocking indefinitely

    print(f"Successfully opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
    time.sleep(2)  # Give the serial port a moment to fully open

    # Message to send
    message = "Hello from Python via USB serial!\n"

    # Encode the string to bytes before sending (UTF-8 is common)
    ser.write(message.encode('utf-8'))
    print(f"Sent: '{message.strip()}'")

    # Optional: Read a response if the device sends one back
    # This will read up to 100 bytes or until timeout
    response = ser.readline().decode('utf-8').strip()
    if response:
        print(f"Received response: '{response}'")
    else:
        print("No response received within timeout.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    # Close the serial port when done
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")