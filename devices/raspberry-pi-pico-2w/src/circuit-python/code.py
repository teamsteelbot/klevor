from asyncio import create_task, gather, run
from io import StringIO
from traceback import print_exception

from board import (GP0, GP1, GP11, GP13, GP2, LED)
from busio import I2C

from lib.bno08x import BNO08XHandler
from lib.challenge import WithObstacles, WithoutObstacles
from lib.enums import Challenge, QuaternionAxis
from lib.env import Env
from lib.esc_motor import ESCMotorHandler
from lib.led import LEDHandler
from lib.serial_communication import SerialCommunication
from lib.servo import ServoHandler
from lib.switch import SwitchHandler

# Constants
CHUNK_SIZE = 64
MOVEMENT = Env.get_movement_mode()
DEBUG = Env.get_debug_mode()
CHALLENGE = Env.get_challenge()
QUATERNION_HORIZONTAL_AXIS = QuaternionAxis.ROLL

# Pins
I2C_BUS = I2C(GP1, GP0)
ESC_MOTOR_PIN = GP2
SERVO_PIN = GP13
SWITCH_PIN = GP11

# Robot's components handlers
led = LEDHandler(led_pin=LED)
serial_communication = SerialCommunication(
    console_port_enabled=True,
    data_port_enabled=True,
    led=led,
    challenge=CHALLENGE,
)
servo = ServoHandler(servo_pin=SERVO_PIN, movement=MOVEMENT)
motor = ESCMotorHandler(motor_pin=ESC_MOTOR_PIN, movement=MOVEMENT)
bno08x = BNO08XHandler(
    horizontal_axis=QUATERNION_HORIZONTAL_AXIS,
    i2c=I2C_BUS,
    serial_communication=serial_communication
)
switch = SwitchHandler(
    switch_pin=SWITCH_PIN,
    serial_communication=serial_communication,
    led=led
)


async def main():
    """
    Main function to initialize the robot and start the main algorithm.
    """
    global bno08x, servo, motor, serial_communication, switch

    try:
        # Create tasks for initialization
        bno08x_calibrate = create_task(bno08x.calibrate())
        motor_stop = create_task(motor.stop())
        servo_center = create_task(servo.center())

        # Wait for all initialization tasks to complete
        await gather(bno08x_calibrate, motor_stop, servo_center)

        # Wait for the switch to be pressed
        await switch.wait()

        # Start the challenge based on the challenge type
        if CHALLENGE == Challenge.WITH_OBSTACLES:
            # Initialize the WithObstacles challenge handler
            with_obstacles = WithObstacles(
                bno08x=bno08x,
                servo=servo,
                motor=motor,
                serial_communication=serial_communication
            )

            # Start the main loop for the challenge with obstacles
            await with_obstacles.loop()

        elif CHALLENGE == Challenge.WITHOUT_OBSTACLES:
            # Initialize the WithoutObstacles challenge handler
            without_obstacles = WithoutObstacles(
                bno08x=bno08x,
                servo=servo,
                motor=motor,
                serial_communication=serial_communication
            )

            # Start the main loop for the challenge without obstacles
            await without_obstacles.loop()

        else:
            raise ValueError(f"Unsupported challenge type: {CHALLENGE}")

    except Exception as e:
        # Get the traceback as string
        buf = StringIO()
        print_exception(e, e, e.__traceback__, file=buf)
        tb_str = buf.getvalue()
    
        # Send error message to the serial communication
        tb_len = len(tb_str)
        for i in range(0, tb_len+1, CHUNK_SIZE):
            is_last = (i + CHUNK_SIZE) >= tb_len+1
            chunk = tb_str[i:i+CHUNK_SIZE] if not is_last else tb_str[i:i+CHUNK_SIZE-1]
            serial_communication.send_message_by_chunks(chunk, is_last_chunk=is_last)


# Start the asyncio event loop
run(main())