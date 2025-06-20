from usb_cdc import console, data
from board import LED
from digitalio import DigitalInOut, Direction
from time import sleep

from .message import Message, Category, Status, Challenge

class SerialCommunicationError(Exception):
    """
    Custom exception class for serial communication errors.
    """
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return f"SerialCommunicationError: {self.msg}"

class SerialCommunication:
    """
    A class to handle serial communication over USB CDC in CircuitPython.
    """
    # Default configuration
    TOGGLE_LED_ON_RECEIVE = False
    DATA_PORT_ENABLED = True
    CONSOLE_PORT_ENABLED = True
    TOGGLE_LED_DELAY = 0.001

    # Status messages
    START_MESSAGE = Message(Category.STATUS, Status.START.get_status_name())
    STOP_MESSAGE = Message(Category.STATUS, Status.STOP.get_status_name())
    OK_MESSAGE = Message(Category.STATUS, Status.OK.get_status_name())

    # Challenge messages
    CHALLENGE_WITH_OBSTACLES = Message(Category.CHALLENGE, Challenge.WITH_OBSTACLES.get_challenge_name())
    CHALLENGE_WITHOUT_OBSTACLES = Message(Category.CHALLENGE, Challenge.WITHOUT_OBSTACLES.get_challenge_name())

    def __init__(self, console_port_enabled: bool = CONSOLE_PORT_ENABLED, data_port_enabled: bool = DATA_PORT_ENABLED,
                 toggle_led_on_receive: bool = TOGGLE_LED_ON_RECEIVE, challenge: Challenge = Challenge.WITHOUT_OBSTACLES):
        """
        Initialize the SerialCommunication instance.

        Args:
            console_port_enabled (bool): Whether to enable the console port for sending messages.
            data_port_enabled (bool): Whether to enable the data port for receiving messages.
            toggle_led_on_receive (bool): Whether to toggle the onboard LED when a message is received.
            challenge (Challenge): The challenge type for the robot.
        """
        self.__data_port = data if data_port_enabled else None
        self.__console_port = console if console_port_enabled else None
        self.__toggle_led_on_receive = toggle_led_on_receive

        # Send the challenge message
        if self.__console_port:
            challenge_message = self.CHALLENGE_WITH_OBSTACLES if challenge == Challenge.WITH_OBSTACLES else self.CHALLENGE_WITHOUT_OBSTACLES
            self.send_message(challenge_message)

        # Initialize LED if toggling is enabled
        if not self.__toggle_led_on_receive:
            self.__led = None
            return

        self.__led = DigitalInOut(LED)
        self.__led.direction = Direction.OUTPUT

    def receive_message(self) -> Message|None:
        """
        Receive a message from the USB CDC data stream.

        Returns:
            Message|None: The received message, or None if no message is available.
        """
        if not self.__data_port:
            raise SerialCommunicationError("Data port is not enabled.")

        if self.__data_port.in_waiting > 0:
            msg_str = self.__data_port.readline().strip().decode("utf-8")
            msg = Message.from_string(msg_str)

            if self.__toggle_led_on_receive and self.__led:
                # Toggle the LED to indicate data reception
                self.__led.value = True
                sleep(self.TOGGLE_LED_DELAY)
                self.__led.value = False

            return msg

    def send_message(self, message: Message):
        """
        Send a message to the USB CDC console stream.

        Args:
            message (Message): The message to send.
        """
        if not self.__console_port:
            raise SerialCommunicationError("Console port is not enabled.")

        try:
            self.__console_port.write(str(message).encode("utf-8"))

        except Exception as e:
            raise SerialCommunicationError(f"Error sending message: {e}")