from time import sleep

from lib.esc_motor import ESCMotorHandler

# Create an instance of the ESCMotorHandler
motor_handler = ESCMotorHandler()

motor_handler.speed = 0
sleep(1)

# Test different speeds
i = 0.5
while i >= -0.5:
    # Set the motor speed
    motor_handler.speed = i
    print(i)
    i -= 0.1

    # Wait a bit to observe the speed change
    sleep(0.2)

motor_handler.speed = 0
