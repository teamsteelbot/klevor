from usb_cdc import console, data
from board import LED
from digitalio import DigitalInOut, Direction
from time import monotonic

from .led import LEDHandler
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

    # Status messages
    START_MESSAGE = Message(Category.STATUS, Status.START.get_status_name())
    STOP_MESSAGE = Message(Category.STATUS, Status.STOP.get_status_name())
    OK_MESSAGE = Message(Category.STATUS, Status.OK.get_status_name())

    # Challenge messages
    CHALLENGE_WITH_OBSTACLES = Message(Category.CHALLENGE, Challenge.WITH_OBSTACLES.get_challenge_name())
    CHALLENGE_WITHOUT_OBSTACLES = Message(Category.CHALLENGE, Challenge.WITHOUT_OBSTACLES.get_challenge_name())

    # Confirmation timeout
    CONFIRMATION_TIMEOUT = 30.0

    def __init__(self, console_port_enabled: bool = CONSOLE_PORT_ENABLED, data_port_enabled: bool = DATA_PORT_ENABLED,
                 challenge: Challenge = Challenge.WITHOUT_OBSTACLES, led: LEDHandler = None):
        """
        Initialize the SerialCommunication instance.

        Args:
            console_port_enabled (bool): Whether to enable the console port for sending messages.
            data_port_enabled (bool): Whether to enable the data port for receiving messages.
            challenge (Challenge): The challenge type for the robot.
            led (LEDHandler | None): Optional LED handler for toggling the LED on message receive.
        """
        self.__console_port = console if console_port_enabled else None
        self.__data_port = data if data_port_enabled else None
        self.__challenge = challenge
        self.__led = led

    async def receive_message(self) -> list[Message] | None:
        """
        Receive a message from the USB CDC data stream.

        Returns:
            Message | None: The received message, or None if no message is available.
        """
        if not self.__data_port:
            raise SerialCommunicationError("Data port is not enabled.")

        if self.__data_port.in_waiting == 0:
            # Turn off the LED if no data is waiting
            if self.__led and self.__led.is_on():
                self.__led.off()
            return None

        # Turn on the LED to indicate a message has been received
        if self.__led and self.__led.is_off():
            self.__led.on()

        msgs = []
        while self.__data_port.in_waiting > 0:
            # Read a line from the data port
            msg_str = self.__data_port.readline().strip().decode("utf-8")

            try:
                msg = Message.from_string(msg_str)
                msgs.append(msg)

            except ValueError as e:
                raise SerialCommunicationError(f"Invalid message format: {msg_str}") from e

        return msgs

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

    async def wait_for_confirmation(self, timeout: float = CONFIRMATION_TIMEOUT) -> bool:
        """
        Wait for a confirmation message from the console port.

        Args:
            timeout (float): The maximum time to wait for a confirmation message.

        Returns:
            bool: True if confirmation received, False if timeout.
        """
        start_time = monotonic()
        while monotonic() - start_time < timeout:
            msg = await self.receive_message()
            if msg and msg.category == Category.STATUS and msg.content == Status.OK.get_status_name():
                return True
        return False

    def send_challenge_message(self):
        """
        Send a challenge message to the console port.
        """
        challenge_message = self.CHALLENGE_WITH_OBSTACLES if self.__challenge == Challenge.WITH_OBSTACLES else self.CHALLENGE_WITHOUT_OBSTACLES
        self.send_message(challenge_message)

    def start(self):
        """
        Send the start message to the console port and wait for confirmation.
        """
        # Send the start message
        self.send_message(self.START_MESSAGE)

        # Wait for confirmation of the start message
        if not self.wait_for_confirmation():
            raise SerialCommunicationError("Failed to receive confirmation for start message.")
