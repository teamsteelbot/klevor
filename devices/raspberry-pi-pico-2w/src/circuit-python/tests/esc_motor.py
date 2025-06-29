from asyncio import run
from time import sleep

from board import GP2
from lib.env import Env
from lib.esc_motor import ESCMotorHandler

# Constants
MOVEMENT = Env.get_movement_mode()

# Pins
ESC_MOTOR_PIN = GP2

# Create an instance of the ESCMotorHandler
motor_handler = ESCMotorHandler(
    motor_pin=ESC_MOTOR_PIN,
    movement=MOVEMENT
)

run(motor_handler.set_speed(0))
sleep(2)

# Test different speeds
i = 0.5
while i >=  -0.5:
    # Set the motor speed
    run(motor_handler.set_speed(i))
    print(i)
    i -= 0.01

run(motor_handler.set_speed(0))