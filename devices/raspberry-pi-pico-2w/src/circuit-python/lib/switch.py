from board import GP11
from digitalio import DigitalInOut, Direction, Pull
from asyncio import sleep

from .led import LEDHandler
from .serial_communication import SerialCommunication

class SwitchHandler:
    """
    A class to handle a switch connected to a Raspberry Pi Pico.
    """
    # Default configuration
    SWITCH_PIN = GP11
    DELAY = 0.01

    def __init__(self, switch_pin: int = SWITCH_PIN, serial_communication: SerialCommunication = None,
                 led: LEDHandler = None):
        """
        Initializes the switch handler with the specified pin.

        Args:
            switch_pin (int): The GPIO number where the switch is connected.
            serial_communication (SerialCommunication | None): Optional serial communication handler.
            led (LEDHandler | None): Optional LED handler for visual feedback when the switch is pressed.
        """
        # Set up the switch pin as input with pull-up resistor
        self.__switch = DigitalInOut(switch_pin)
        self.__switch.direction = Direction.INPUT
        self.__switch.pull = Pull.UP

        # If serial communication is provided, set it
        self.__serial_communication = serial_communication

        # If LED handler is provided, set it
        self.__led = led

    async def wait(self):
        """
        Waits for the switch to be pressed.

        This method blocks until the switch is pressed (i.e., the pin reads LOW).
        """
        while self.__switch.value:
            await sleep(self.DELAY)

        # If serial communication is provided, signal the start
        if self.__serial_communication:
            self.__serial_communication.start()

        # Blink the LED if provided
        if self.__led:
            await self.__led.blink()