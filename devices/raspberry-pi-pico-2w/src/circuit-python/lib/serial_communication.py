from usb_cdc import console, data
from board import LED
from digitalio import DigitalInOut, Direction
from time import monotonic

from .led import LEDHandler
from .message import IncomingMessage, IncomingCategory, OutgoingMessage, OutgoingCategory, Status, Request
from .env import Challenge

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
    START_MESSAGE = OutgoingMessage(OutgoingCategory.STATUS, Status.START.get_name())
    STOP_MESSAGE = OutgoingMessage(OutgoingCategory.STATUS, Status.STOP.get_name())
    OK_MESSAGE = IncomingMessage(IncomingCategory.STATUS, Status.OK.get_name())

    # Challenge messages
    CHALLENGE_WITH_OBSTACLES = OutgoingMessage(OutgoingCategory.CHALLENGE, Challenge.WITH_OBSTACLES.get_challenge_name())
    CHALLENGE_WITHOUT_OBSTACLES = OutgoingMessage(OutgoingCategory.CHALLENGE, Challenge.WITHOUT_OBSTACLES.get_challenge_name())

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

    async def receive_messages(self) -> list[IncomingMessage] | None:
        """
        Receive messages from the USB CDC data stream.

        Returns:
            list[IncomingMessage] | None: A list of received messages or None if no messages are waiting.
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
                msg = IncomingMessage.from_string(msg_str)
                msgs.append(msg)

            except ValueError as e:
                raise SerialCommunicationError(f"Invalid message format: {msg_str}") from e

        return msgs

    def send_message(self, message: OutgoingMessage):
        """
        Send a message to the USB CDC console stream.

        Args:
            message (OutgoingMessage): The message to send.
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
            msgs = await self.receive_messages()
            for msg in msgs:
                # If the message is a confirmation message, return True
                if msg and msg.category == IncomingCategory.STATUS and msg.content == Status.OK.get_name():
                    return True
        return False

    async def send_challenge_message(self):
        """
        Send a challenge message to the console port.
        """
        # Send the challenge message based on the challenge type
        challenge_message = self.CHALLENGE_WITH_OBSTACLES if self.__challenge == Challenge.WITH_OBSTACLES else self.CHALLENGE_WITHOUT_OBSTACLES
        self.send_message(challenge_message)

        # Wait for confirmation of the challenge message
        if not await self.wait_for_confirmation():
            raise SerialCommunicationError("Failed to receive confirmation for challenge message.")

    def send_motor_speed_message(self, speed: float):
        """
        Send a motor speed message to the console port.

        Args:
            speed (float): The speed value to send.
        """
        motor_message = OutgoingMessage(OutgoingCategory.MOTOR_SPEED, str(speed))
        self.send_message(motor_message)

    def send_servo_angle_message(self, angle: int):
        """
        Send a servo angle message to the console port.

        Args:
            angle (int): The angle value to send.
        """
        servo_message = OutgoingMessage(OutgoingCategory.SERVO_ANGLE, str(angle))
        self.send_message(servo_message)

    def send_bno08x_turns_message(self, turns: int):
        """
        Send a BNO08x turns message to the console port.

        Args:
            turns (int): The number of turns to send.
        """
        bno08x_message = OutgoingMessage(OutgoingCategory.BNO08X_TURNS, str(turns))
        self.send_message(bno08x_message)

    def send_error_message(self, error: Exception):
        """
        Send an error message to the console port.

        Args:
            error (Exception): The error to send.
        """
        error_message = OutgoingMessage(OutgoingCategory.ERROR, str(error))
        self.send_message(error_message)

    async def start(self):
        """
        Send the start message to the console port and wait for confirmation.
        """
        # Send the start message
        self.send_message(self.START_MESSAGE)

        # Wait for confirmation of the start message
        if not await self.wait_for_confirmation():
            raise SerialCommunicationError("Failed to receive confirmation for start message.")

    async def stop(self):
        """
        Send the stop message to the console port and wait for confirmation.
        """
        # Send the stop message
        self.send_message(self.STOP_MESSAGE)

        # Wait for confirmation of the stop message
        if not await self.wait_for_confirmation():
            raise SerialCommunicationError("Failed to receive confirmation for stop message.")

        # Turn off the LED if it was toggled on receive
        if self.__led:
            self.__led.off()