from board import GP11
from digitalio import DigitalInOut, Direction, Pull
from time import sleep

class SwitchHandler:
    """
    A class to handle a switch connected to a Raspberry Pi Pico.
    """
    # Default configuration
    SWITCH_PIN = GP11
    DELAY = 0.01

    def __init__(self, switch_pin: int = SWITCH_PIN):
        """
        Initializes the switch handler with the specified pin.

        Args:
            switch_pin (int): The GPIO number where the switch is connected.
        """
        # Set up the switch pin as input with pull-up resistor
        self.__switch = DigitalInOut(switch_pin)
        self.__switch.direction = Direction.INPUT
        self.__switch.pull = Pull.UP

    def wait_for_switch(self):
        """
        Waits for the switch to be pressed.

        This method blocks until the switch is pressed (i.e., the pin reads LOW).
        """
        while self.__switch.value:
            sleep(self.DELAY)