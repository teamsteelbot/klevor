import serial
import time

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
