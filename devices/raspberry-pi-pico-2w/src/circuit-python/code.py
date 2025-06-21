from board import (LED, GP0, GP1, GP2, GP11, GP13)
from busio import I2C
from asyncio import run, create_task, gather

from lib.bno08x import BNO08XHandler
from lib.env import Env, Challenge
from lib.esc_motor import ESCMotorHandler
from lib.led import LEDHandler
from lib.serial_communication import SerialCommunication
from lib.servo import ServoHandler
from lib.switch import SwitchHandler
from lib.message import IncomingCategory, IncomingMessage, RPLIDAR

# Constants
MOVEMENT = Env.get_movement_mode()
DEBUG = Env.get_debug_mode()
CHALLENGE = Env.get_challenge()

# Distance constants
FRONT_DISTANCE_THRESHOLD = 500
SIDE_DISTANCE_DIFFERENCE_PERCENTAGE = 0.2
SIDE_DISTANCE_THRESHOLD = 1500
STOP_DISTANCE_THRESHOLD = 1500
TARGET_DISTANCE_STOP_START = 200

# Pins
I2C_BUS = I2C(GP1, GP0)
ESC_MOTOR_PIN = GP2
SERVO_PIN = GP13
SWITCH_PIN = GP11

# Robot's components handlers
led: LEDHandler = LEDHandler(led_pin=LED)
serial_communication: SerialCommunication = SerialCommunication(console_port_enabled=True, data_port_enabled=True,
                                                                led=led)
servo: ServoHandler = ServoHandler(servo_pin=SERVO_PIN, serial_communication=serial_communication)
motor: ESCMotorHandler = ESCMotorHandler(motor_pin=ESC_MOTOR_PIN, serial_communication=serial_communication,
                                         movement=MOVEMENT)
bno08x: BNO08XHandler = BNO08XHandler(i2c=I2C_BUS, serial_communication=serial_communication)
switch: SwitchHandler = SwitchHandler(switch_pin=SWITCH_PIN, serial_communication=serial_communication, led=led)

async def challenge_with_obstacles():
    """
    Challenge with obstacles logic.
    This function will be executed when the robot is set to challenge mode with obstacles.
    """
    global bno08x, servo, motor, serial_communication

    while True:
        break

async def challenge_without_obstacles_calculate_distance(msgs: list[IncomingMessage]) -> tuple[float, float, float]:
    """
    Calculate the average distances from the received RPLIDAR messages.

    Args:
        msgs (list[IncomingMessage]): List of incoming messages from the serial communication.
    Returns:
        tuple[float, float, float]: Average distances for front, left, and right.
    """
    # Initialize average distances
    avg_front_dist = 0.0
    avg_left_dist = 0.0
    avg_right_dist = 0.0

    # Process the received messages (must be only RPLIDAR messages) on reverse order
    for msg in msgs[::-1]:
        if msg.category == IncomingCategory.RPLIDAR:
            # Split the message content to extract distance
            parts = msg.content.split(IncomingMessage.CONTENT_HEADER_SEPARATOR)

            # Check the type of distance
            if parts[0] == RPLIDAR.FRONT:
                avg_front_dist = float(parts[1])

            elif parts[0] == RPLIDAR.LEFT:
                avg_left_dist = float(parts[1])

            elif parts[0] == RPLIDAR.RIGHT:
                avg_right_dist = float(parts[1])

    return avg_front_dist, avg_left_dist, avg_right_dist

async def challenge_without_obstacles():
    """
    Challenge without obstacles logic.
    This function will be executed when the robot is set to challenge mode without obstacles.
    """
    global bno08x, servo, motor, serial_communication

    # Set the last known turns to zero
    last_known_turns = 0

    while True:
        # Create the update quaternion and receive serial messages tasks
        update_quaternion_task = create_task(bno08x.update_quaternion())
        receive_serial_task = create_task(serial_communication.receive_messages())

        # Wait for the tasks to complete
        results = await gather(update_quaternion_task, receive_serial_task)
        msgs = results[1]

        # Process the received messages (must be only RPLIDAR messages) on reverse order
        avg_front_dist, avg_left_dist, avg_right_dist = await challenge_without_obstacles_calculate_distance(msgs)

        # Algorithm tasks
        tasks = []

        # Check for the current turn and center the servo if necessary
        if servo.is_turning() and bno08x.turns != last_known_turns:
            tasks.append(create_task(servo.center()))

            # Update for the next check
            last_known_turns = bno08x.turns

        # Overall Mission Completion Check
        if last_known_turns == 12:
            tasks.append(create_task(motor.set_speed(motor.SPEED_NORMAL)))

            # Gather the tasks and wait for them to complete
            await gather(*tasks)

            while True:
                # Receive messages from the serial communication
                msgs = await serial_communication.receive_messages()

                # Process the received messages (must be only RPLIDAR messages) on reverse order
                avg_front_dist, avg_left_dist, avg_right_dist = await challenge_without_obstacles_calculate_distance(
                    msgs)

                if avg_front_dist <= STOP_DISTANCE_THRESHOLD:
                    await motor.stop()
                    await serial_communication.stop()
                    return

        # Check if the robot should move forward or turn
        if avg_front_dist >= FRONT_DISTANCE_THRESHOLD:
            tasks.append(create_task(motor.set_speed(motor.SPEED_NORMAL)))

            # Check if the servo should make a little turn to the left or right in order to center the robot
            if avg_right_dist >= avg_left_dist * (1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                tasks.append(create_task(servo.right(servo.SMALL_TURN_ANGLE)))

            elif avg_left_dist >= avg_right_dist * (1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                tasks.append(create_task(servo.left(servo.SMALL_TURN_ANGLE)))

            else:
                tasks.append(create_task(servo.center()))

        else:
            tasks.append(create_task(motor.set_speed(motor.SPEED_SLOW)))

            # Check if the robot should turn left or right based on the side distances
            if avg_right_dist >= SIDE_DISTANCE_THRESHOLD:
                tasks.append(create_task(servo.right(servo.BIG_TURN_ANGLE)))

            elif avg_left_dist >= SIDE_DISTANCE_THRESHOLD:
                tasks.append(create_task(servo.left(servo.BIG_TURN_ANGLE)))

        # Gather the tasks and wait for them to complete
        if tasks:
            await gather(*tasks)

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
            await challenge_with_obstacles()

        elif CHALLENGE == Challenge.WITHOUT_OBSTACLES:
            await challenge_without_obstacles()

        else:
            raise ValueError(f"Unsupported challenge type: {CHALLENGE}")

    except Exception as e:
        # Send error message to the serial communication
        serial_communication.send_error_message(e)

# Start the asyncio event loop
run(main())