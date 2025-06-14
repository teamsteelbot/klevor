import board
import time
import digitalio
import usb_cdc

data_port = usb_cdc.data
led_pin = digitalio.DigitalInOut(board.LED)
led_pin.direction = digitalio.Direction.OUTPUT

print("CircuitPython is ready for USB data communication.")
print("Check your host computer for a second serial port for data_port.")

send_counter = 0
def send_data():
    global send_counter
    message = f"Hello from CircuitPython! Counter: {send_counter}\n"
    data_port.write(message.encode('utf-8'))
    print(f"Sent: {message.strip()}")
    send_counter += 1

def receive_data():
    if data_port.in_waiting > 0:
        # Turn on the LED fast to indicate data reception
        led_pin.value = True
        time.sleep(0.1)
        led_pin.value = False

        received_bytes = data_port.read(data_port.in_waiting)
        received_string = received_bytes.decode('utf-8').strip()
        print(f"Received: {received_string}")
        return received_string
    return None

while True:
    send_data()

    # Check for incoming data
    receive_data()
