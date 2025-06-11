from machine import Pin
import time

# For Raspberry Pi Pico W, the onboard LED is connected to the wireless chip
# and is accessed using the string "LED"
led = Pin("LED", Pin.OUT)

while True:
    led.on()
    print("LED is on")
    time.sleep(1)
    led.off()
    print("LED is off")
    time.sleep(1)
