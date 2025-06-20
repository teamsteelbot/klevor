from board import LED
from digitalio import DigitalInOut, Direction

class LED:
    """
    Class handler for the Raspberry Pi Pico onboard LED.
    """

    def __init__(self, led_pin: int):
        """
        Initialize the LED handler.

        Args:
            led_pin (int): The GPIO pin number for the onboard LED.
        """
        self.led = DigitalInOut(LED)
        self.led.direction = Direction.OUTPUT

    def on(self) -> None:
        """Turn the LED on."""
        self.led.value = True

    def off(self) -> None:
        """Turn the LED off."""
        self.led.value = False

    def toggle(self) -> None:
        """Toggle the LED state."""
        self.led.value = not self.led.value