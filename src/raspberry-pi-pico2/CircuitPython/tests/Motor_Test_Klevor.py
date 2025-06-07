import board
import pwmio
import busio
import math
import time
import adafruit_vl53l0x
import digitalio
from adafruit_motor import servo

DEBUG_MODE = 1

ESC_Motor_Pin = board.GP21

ESC_PWM_Configuration = pwmio.PWMOut(ESC_Motor_Pin, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)

def arm_esc():
    if DEBUG_MODE == 1:
        print("Arming ESC... (REMOVE PROPELLERS OR ENSURE MOTOR IS CLEAR AND SECURE!)")
    ESC.throttle = 0.0 # Set throttle to minimum
    time.sleep(2) # Give ESC time to recognize minimum

    if DEBUG_MODE == 1:
        print("Sending max throttle signal...")
    ESC.throttle = -0.5 # Send throttle to maximum
    time.sleep(2) # Give ESC time to recognize maximum

    if DEBUG_MODE == 1:
        print("Sending stop signal to complete arming...")
    ESC.throttle = 0.0 # Return throttle to minimum/stop
    time.sleep(1) # Give ESC time to arm

    if DEBUG_MODE == 1:
        print("ESC should now be armed and ready.")
    
while True:
    arm_esc()