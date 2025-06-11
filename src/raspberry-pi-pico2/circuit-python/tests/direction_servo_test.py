#-----------------------------LIBRARIES-----------------------------
import board
import pwmio
import busio
import math
import time
import adafruit_vl53l0x
import digitalio
from adafruit_motor import servo
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)

SERVO_PIN = board.GP18

Servo_PWM_Configuration = pwmio.PWMOut(SERVO_PIN, duty_cycle=0, frequency=50)
Direction_Servo = servo.Servo(Servo_PWM_Configuration, actuation_range=180, min_pulse=500, max_pulse=2500)

def set_steering_angle(angle):
    Direction_Servo.angle = max(0, min(180, angle))
    
while True:
    set_steering_angle(81)
    time.sleep(5)
    set_steering_angle(110)
    time.sleep(5)
    set_steering_angle(44)
    time.sleep(5)