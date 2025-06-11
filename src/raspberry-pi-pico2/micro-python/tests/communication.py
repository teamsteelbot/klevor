import machine
import time

uart = machine.UART(0, baudrate=115200) # Or your desired baud rate

while True:
    uart.write("Hello from Pico!\n")
    time.sleep(1)

    if uart.any():
        received_data = uart.readline()
        print(f"Received from Pi: {received_data.decode('utf-8').strip()}")
