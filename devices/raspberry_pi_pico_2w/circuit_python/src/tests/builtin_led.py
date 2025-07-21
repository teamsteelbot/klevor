from time import sleep

from board import LED
from digitalio import DigitalInOut, Direction

# Set up the onboard LED on the Raspberry Pi Pico
led = DigitalInOut(LED)
led.direction = Direction.OUTPUT

# Blink the LED indefinitely
while True:
	led.value = True
	sleep(1)
	led.value = False
	sleep(1)
