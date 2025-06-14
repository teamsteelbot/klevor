import usb_cdc
from time import sleep
from board import LED
from digitalio import DigitalInOut, Direction
import asyncio
import os
import ipaddress
import wifi
import socketpool

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

def get_global_variable_safely(var_name):
    """
    Safely get a global variable by name.
    Returns None if the variable does not exist.
    """
    try:
        return globals()[var_name]
    except KeyError:
        return None

async def connect_wifi(attempts=5):
    """
    Connect to WiFi using credentials from environment variables.
    """
    global wifi_enabled

    # Initialize Wi-Fi status
    wifi_enabled = False  
    counter = 0
    while not wifi.radio.ipv4_address and counter < attempts:  # Loop until connected
        try:
            wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
            print("Connected to WiFi!")
            print("Pico 2W IP Address:", wifi.radio.ipv4_address)
            #print("Gateway:", wifi.radio.ipv4_gateway)
            #print("DNS Server:", wifi.radio.ipv4_dns)

            wifi_enabled = True

        except Exception as e:
            print(f"Error connecting to WiFi: {e}. Retrying in 5 seconds...")
        await asyncio.sleep(5)  # Use asyncio.sleep for non-blocking delay

        counter += 1

def create_socket_pool():
    """
    Create a socket pool for creating sockets.
    This must be done AFTER Wi-Fi is connected.
    """
    global pool

    if not get_global_variable_safely('wifi_enabled'):
        print("Wi-Fi is not connected. Cannot create socket pool.")
        return None

    try:
        pool = socketpool.SocketPool(wifi.radio)
        print("Socket pool created successfully.")
        return pool
    except Exception as e:
        print(f"Error creating socket pool: {e}")
        return None

def create_udp_socket():
    """
    Create UDP socket.
    """
    global udp_socket

    if not get_global_variable_safely('pool'):
        print("Socket pool is not available. Cannot create UDP socket.")
        return None
    
    try:
        udp_socket = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
        udp_socket.setblocking(False)  # Set to non-blocking mode
        return udp_socket
    except Exception as e:
        print(f"Error creating UDP socket: {e}")
        return None
    
def close_udp_socket():
    """
    Close UDP socket.
    """
    if not get_global_variable_safely('udp_socket'):
        print("UDP socket is not available. Cannot close.")
        return

    try:
        udp_socket.close()
        print("UDP socket closed.")
    except Exception as e:
        print(f"Error closing UDP socket: {e}")

def get_target_info():
    """
    Get target IP and port from environment variables.
    """
    global target_ip, target_port

    target_ip = os.getenv("SOCKET_SERVER_IP")
    if not target_ip:
        raise ValueError("SOCKET_SERVER_IP environment variable is not set.")
    target_port = int(os.getenv("SOCKET_SERVER_PORT"))
    if not target_port:
        raise ValueError("SOCKET_SERVER_PORT environment variable is not set.")
    
    try:
        ipaddress.ip_address(target_ip)  # Validate IP address format
    except ValueError as e:
        raise ValueError(f"Invalid TARGET_IP: {e}")
    return target_ip, target_port

async def send_udp_message(target_host, target_port, message):
    """
    Send message over UDP
    """
    if not get_global_variable_safely('udp_socket'):
        print("UDP socket is not available. Cannot send message.")
        return

    try:
        udp_socket.sendto(message.encode('utf-8'), (target_host, target_port))
        print(f"Sent message: '{message}' to {target_host}:{target_port}")
    except OSError as e:
        print(f"Error sending message: {e}. (Non-blocking, continuing)")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def send_udp_message_to_target(message):
    """
    Send a message to the target host and port.
    """
    if not get_global_variable_safely('target_ip') or not get_global_variable_safely('target_port'):
        print("Target IP or port is not set. Cannot send message.")
        return

    await send_udp_message(target_ip, target_port, message)

async def setup():
    """
    Setup the Raspberry Pi Pico pins.
    """
    global led
    
    # Initialize the built-in LED on the Raspberry Pi Pico
    led = DigitalInOut(LED)
    led.direction = Direction.OUTPUT

    """
    Main function to run the UDP sender.
    """
    # First, ensure Wi-Fi connection
    await connect_wifi()

    # Create a socket pool after Wi-Fi is connected
    create_socket_pool()

    # Create UDP socket
    udp_socket = create_udp_socket()

    # Get target IP and port from environment variables
    get_target_info()
    
    # Send a test message
    message = "Hello from Raspberry Pi Pico 2W!"
    await send_udp_message_to_target(message)

    # Close the UDP socket when done
    close_udp_socket()

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
        message = usb_cdc.data.readline().strip().decode("utf-8")

        # Send that the given message was received
        send_message("received_message: " + message)
        return message
    
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

# Initialize it
asyncio.run(setup())

# Send start message to the device
#send_message(START_MESSAGE)
#print("Sent: " + START_MESSAGE)
#wait_for_confirmation(START_MESSAGE)

# Read N times
read_times = 0
while read_times < READ_TIMES_LIMIT:
    message_received = receive_message()
    if message_received:
        print("Received: " + str(message_received))
    
    #read_times += 1
    sleep(READ_DELAY)

# Send stop message to the device
#send_message(STOP_MESSAGE)
#print("Sent: " + STOP_MESSAGE)
#wait_for_confirmation(STOP_MESSAGE)
