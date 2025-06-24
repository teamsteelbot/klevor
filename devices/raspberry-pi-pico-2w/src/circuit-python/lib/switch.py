from board import GP11
from digitalio import DigitalInOut, Direction, Pull
from asyncio import sleep, create_task, gather

from .led import LEDHandler
from .serial_communication import SerialCommunication

class SwitchHandler:
    """
    A class to handle a switch connected to a Raspberry Pi Pico.
    """
    # Default configuration
    SWITCH_PIN = GP11
    DELAY = 0.01

    def __init__(self, serial_communication: SerialCommunication, switch_pin: int = SWITCH_PIN,
                 led: LEDHandler = None):
        """
        Initializes the switch handler with the specified pin.

        Args:
            serial_communication (SerialCommunication): Serial communication handler.
            switch_pin (int): The GPIO number where the switch is connected.
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

        # Create the tasks to signal the start of the robot's operation
        start_tasks = [create_task(self.__serial_communication.start())]

        # Blink the LED if provided
        if self.__led:
            start_tasks.append(create_task(self.__led.blink()))

        # Wait for all start tasks to complete
        await gather(*start_tasks)