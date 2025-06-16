from usb_cdc import console, data
from board import LED
from digitalio import DigitalInOut, Direction
from time import sleep

class SerialCommunicationError(Exception):
    """
    Custom exception class for serial communication errors.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"SerialCommunicationError: {self.message}"

class SerialCommunication:
    """
    A class to handle serial communication over USB CDC in CircuitPython.
    """
    # Default configuration
    TOGGLE_LED_ON_RECEIVE = False
    DATA_PORT_ENABLED = True
    CONSOLE_PORT_ENABLED = True
    TOGGLE_LED_DELAY = 0.001

    def __init__(self, console_port_enabled: bool = CONSOLE_PORT_ENABLED, data_port_enabled: bool = DATA_PORT_ENABLED, toggle_led_on_receive: bool = TOGGLE_LED_ON_RECEIVE):
        """
        Initialize the SerialCommunication instance.
        """
        self.__data_port = data if data_port_enabled else None
        self.__console_port = console if console_port_enabled else None
        self.__toggle_led_on_receive = toggle_led_on_receive

        # Initialize LED if toggling is enabled
        if not self.__toggle_led_on_receive:
            self.__led = None
            return

        self.__led = DigitalInOut(LED)
        self.__led.direction = Direction.OUTPUT

    def receive_message(self) -> str|None:
        """
        Receive a message from the USB CDC data stream.
        Returns:
            str|None: The received message as a string, or None if no message is available.
        """
        if not self.__data_port:
            raise SerialCommunicationError("Data port is not enabled.")

        if self.__data_port.in_waiting > 0:
            message = self.__data_port.readline().strip().decode("utf-8")
            if self.__toggle_led_on_receive and self.__led:
                # Toggle the LED to indicate data reception
                self.__led.value = True
                sleep(self.TOGGLE_LED_DELAY)
                self.__led.value = False

            return message

    def send_message(self, message: str):
        """
        Send a message to the USB CDC console stream.

        Args:
            message (str): The message to send.
        """
        if not self.__console_port:
            raise SerialCommunicationError("Console port is not enabled.")

        try:
            self.__console_port.write((message + "\n").encode("utf-8"))

        except Exception as e:
            raise SerialCommunicationError(f"Error sending message: {e}")