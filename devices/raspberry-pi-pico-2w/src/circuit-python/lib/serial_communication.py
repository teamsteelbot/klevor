from time import monotonic

from usb_cdc import console, data

from .enums import Challenge, Status
from .led import LEDHandler
from .message import (
    IncomingCategory,
    IncomingMessage,
    OutgoingCategory,
    OutgoingMessage,
    END_CHAR
)


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
    START_MESSAGE = OutgoingMessage(
        OutgoingCategory.STATUS,
        Status.START
    )
    STOP_MESSAGE = IncomingMessage(
        OutgoingCategory.STATUS,
        Status.STOP
    )
    INCOMING_OK_MESSAGE = IncomingMessage(
        IncomingCategory.STATUS,
        Status.OK
    )
    OUTGOING_OK_MESSAGE = OutgoingMessage(
        OutgoingCategory.STATUS,
        Status.OK
    )
    HEARTBEAT_MESSAGE = OutgoingMessage(
        OutgoingCategory.STATUS,
        Status.HEARTBEAT
    )

    # Challenge messages
    CHALLENGE_WITH_OBSTACLES = OutgoingMessage(
        OutgoingCategory.CHALLENGE,
        Challenge.WITH_OBSTACLES
    )
    CHALLENGE_WITHOUT_OBSTACLES = OutgoingMessage(
        OutgoingCategory.CHALLENGE,
        Challenge.WITHOUT_OBSTACLES
    )

    # Confirmation timeout
    CONFIRMATION_TIMEOUT = 5.0

    def __init__(
        self,
        challenge: str,
        console_port_enabled: bool = CONSOLE_PORT_ENABLED,
        data_port_enabled: bool = DATA_PORT_ENABLED,
        led: LEDHandler = None
    ):
        """
        Initialize the SerialCommunication instance.

        Args:
            challenge (str): The challenge type for the robot.
            console_port_enabled (bool): Whether to enable the console port for sending messages.
            data_port_enabled (bool): Whether to enable the data port for receiving messages.
            led (LEDHandler | None): Optional LED handler for toggling the LED on message receive.
        """
        self.__console_port = console if console_port_enabled else None
        self.__data_port = data if data_port_enabled else None
        self.__challenge = challenge
        self.__led = led

    async def receive_messages(self) -> list[IncomingMessage] | []:
        """
        Receive messages from the USB CDC data stream.

        Returns:
            list[IncomingMessage] | []: A list of received messages or None if no messages are waiting.

        Raises:
            SerialCommunicationError: If the data port is not enabled or if there is an error in reading messages.
        """
        if not self.__data_port:
            msg = "Data port is not enabled."
            raise SerialCommunicationError(msg)

        if self.__data_port.in_waiting == 0:
            # Turn off the LED if no data is waiting
            if self.__led and self.__led.is_on():
                self.__led.off()
            return []

        # Turn on the LED to indicate a message has been received
        if self.__led and self.__led.is_off():
            self.__led.on()

        msgs = []
        buffer = b""
        while self.__data_port.in_waiting > 0:
            byte = self.__data_port.read(1)
            if not byte:
                continue
            if byte != END_CHAR.encode("utf-8"):
                buffer += byte
                continue
                
            try:
                msg_str = buffer.decode("utf-8").strip()
                msg = IncomingMessage.from_string(msg_str)
                msgs.append(msg)
                
            except Exception as e:
                raise SerialCommunicationError(
                    f"Invalid message format or undecodable bytes: {buffer} ({e})"
                ) from e
            buffer = b""

        return msgs

    def send_message(self, message: OutgoingMessage):
        """
        Send a message to the USB CDC console stream.

        Args:
            message (OutgoingMessage): The message to send.
        Raises:
            SerialCommunicationError: If the console port is not enabled or if there is an error in sending the message.
        """
        if not self.__console_port:
            msg = "Console port is not enabled."
            raise SerialCommunicationError(msg)

        try:
            self.__console_port.write(str(message).encode("utf-8"))

        except Exception as e:
            raise SerialCommunicationError(f"Error sending message: {e}")
        
    def send_message_by_chunks(self, message: str, is_last_chunk: bool = False):
        """
        Send a message in chunks to the USB CDC console stream.

        Args:
            message (str): The message to send.
            is_last_chunk (bool): Whether this is the last chunk of the message.
        Raises:
            SerialCommunicationError: If the console port is not enabled or if there is an error in sending the message.
        """
        if not self.__console_port:
            msg = "Console port is not enabled."
            raise SerialCommunicationError(msg)

        try:
            if is_last_chunk:
                self.__console_port.write((message + END_CHAR).encode("utf-8"))
            else:
                self.__console_port.write(message.encode("utf-8"))

        except Exception as e:
            raise SerialCommunicationError(f"Error sending message: {e}")

    async def send_confirmation_message(self):
        """
        Sends a confirmation message through the data port.
        """
        self.send_message(self.OUTGOING_OK_MESSAGE)

    async def wait_for_confirmation_message(
        self,
        msg_to_confirm: OutgoingMessage,
        timeout: float = CONFIRMATION_TIMEOUT
    ) -> None:
        """
        Wait for a confirmation message from the console port.

        Args:
            timeout (float): The maximum time to wait for a confirmation message.
            msg_to_confirm (OutgoingMessage): The message to confirm.
        Raises:
            SerialCommunicationError: If the confirmation message is not received within the timeout period.
        """
        start_time = monotonic()
        while monotonic() - start_time < timeout:
            msgs = await self.receive_messages()
            for msg in msgs:
                if msg == self.INCOMING_OK_MESSAGE:
                    return

        raise SerialCommunicationError(
            f"Confirmation message '{msg_to_confirm.format_to_send_with_error_message()}' not received within {timeout} seconds."
        )
    
    def send_initialization_message(self):
        """
        Send an END_CHAR message to the console port to indicate initialization.
        """
        if not self.__console_port:
            raise SerialCommunicationError("Console port is not enabled.")

        try:
            self.__console_port.write(END_CHAR.encode("utf-8"))

        except Exception as e:
            raise SerialCommunicationError(f"Error sending initialization message: {e}")

    async def send_challenge_message(self):
        """
        Send a challenge message to the console port.

        Raises:
            SerialCommunicationError: If the console port is not enabled or if confirmation is not received.
        """
        # Send the challenge message based on the challenge type
        challenge_message = self.CHALLENGE_WITH_OBSTACLES if self.__challenge == Challenge.WITH_OBSTACLES else self.CHALLENGE_WITHOUT_OBSTACLES
        self.send_message(challenge_message)

        # Wait for confirmation of the challenge message
        await self.wait_for_confirmation_message(challenge_message)

    def send_bno08x_yaw_deg_message(self, yaw_deg: float):
        """
        Send a BNO08x yaw degrees message to the console port.

        Args:
            yaw_deg (float): The yaw value to send.
        """
        bno08x_message = OutgoingMessage(OutgoingCategory.BNO08X_YAW_DEG,
                                         str(yaw_deg))
        self.send_message(bno08x_message)

    def send_bno08x_turns_message(self, turns: int):
        """
        Send a BNO08x turns message to the console port.

        Args:
            turns (int): The number of turns to send.
        """
        bno08x_message = OutgoingMessage(
            OutgoingCategory.BNO08X_TURNS,
            str(turns)
        )
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

        Raises:
            SerialCommunicationError: If the console port is not enabled or if confirmation is not received.
        """
        try:
            # Send the start message
            self.send_message(self.START_MESSAGE)

            # Wait for confirmation of the start message
            await self.wait_for_confirmation_message(self.START_MESSAGE)

        except Exception as e:
            raise e

    async def stop(self):
        """
        Close the serial communication.
        """
        if self.__console_port:
            self.__console_port.deinit()

        if self.__data_port:
            self.__data_port.deinit()

        # Turn off the LED if it exists
        if self.__led:
            self.__led.off()