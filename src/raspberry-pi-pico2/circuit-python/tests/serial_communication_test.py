import usb_cdc
from time import sleep
from board import LED
from digitalio import DigitalInOut, Direction

# Setup LED delay
SETUP_LED_DELAY = 1

# Read delay
READ_DELAY = 0.05

# On error toggle LED delay
LED_TOGGLE_DELAY = 1

# Times to read data before sending stop message
READ_TIMES_LIMIT = 100

# Start and stop message
START_MESSAGE = "status:on"
STOP_MESSAGE = "status:off"

def setup():
    """
    Setup the Raspberry Pi Pico pins.
    """
    global led
    
    # Initialize the built-in LED on the Raspberry Pi Pico
    led = DigitalInOut(LED)
    led.direction = Direction.OUTPUT

    # Start with LED off
    led.value = False  

    # Toggle the LED to indicate that the setup is complete
    led.value = True
    sleep(SETUP_LED_DELAY)
    led.value = False

def on_error():
    """
    Toggle the built-in LED on the Raspberry Pi Pico to indicate an error.
    """
    while True:
        led.value = not led.value  # Toggle LED state
        sleep(LED_TOGGLE_DELAY)  # Wait before toggling again


def receive_message() -> str|None:
    """
    Receive a message from the USB CDC data stream.
    Returns:
        str|None: The received message as a string, or None if no message is available.
    """
    if usb_cdc.data.in_waiting > 0:
        return usb_cdc.data.readline().strip().decode("utf-8")
    
def send_message(message: str):
    """
    Send a message to the USB CDC data stream.
    
    Args:
        message (str): The message to send.
    """
    try:
        usb_cdc.data.write((message + "\n").encode("utf-8"))
    except Exception as e:
        print(f"Error sending message: {e}")
        on_error()

def wait_for_confirmation(message_to_compare: str):
    while True:
        message_received = receive_message()
        if message_received:
            print("Received: " + str(message_received))
            if message_received == message_to_compare:
                break
        
        sleep(READ_DELAY)

# Send start message to the device
send_message(START_MESSAGE)
wait_for_confirmation(START_MESSAGE)

# Read N times
read_times = 0
while read_times < READ_TIMES_LIMIT:
    message_received = receive_message()
    if message_received:
        print("Received: " + str(message_received))
    
    read_times += 1
    sleep(READ_DELAY)

# Send stop message to the device
send_message("status:off")
wait_for_confirmation(STOP_MESSAGE)
