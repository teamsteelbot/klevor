from asyncio import sleep

from board import LED
from digitalio import DigitalInOut, Direction


class LEDHandler:
    """
    A class to manage the onboard LED of the Raspberry Pi Pico 2W.
    """

    def __init__(self, led_pin: int = LED):
        """
        Initializes the LED on the specified GPIO pin.

        Args:
            led_pin (int): The GPIO number where the LED is connected. Default is 25.
        """
        self.__led = DigitalInOut(led_pin)
        self.__led.direction = Direction.OUTPUT

    def on(self):
        """Turns the LED on."""
        self.__led.value = True

    def is_on(self) -> bool:
        """
        Checks if the LED is currently on.

        Returns:
            bool: True if the LED is on, False otherwise.
        """
        return self.__led.value

    def off(self):
        """Turns the LED off."""
        self.__led.value = False

    def is_off(self) -> bool:
        """
        Checks if the LED is currently off.

        Returns:
            bool: True if the LED is off, False otherwise.
        """
        return not self.__led.value

    def toggle(self):
        """Toggles the LED state."""
        self.__led.value = not self.__led.value

    async def blink(self, times: int = 1, delay: float = 0.5):
        """
        Blinks the LED a specified number of times with a delay.

        Args:
            times (int): The number of times to blink the LED. Default is 1.
            delay (float): The delay in seconds between on and off states. Default is 0.5 seconds.
        """
        for _ in range(times):
            self.on()
            await sleep(delay)
            self.off()
            await sleep(delay)
