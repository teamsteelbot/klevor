from asyncio import create_task, gather, run
from io import StringIO
from time import monotonic
from traceback import print_exception

from board import (GP0, GP1, GP11, GP13, GP2, LED)
from busio import I2C

from lib.bno08x import BNO08XHandler
from lib.enums import IncomingCategory, OutgoingCategory
from lib.env import Env
from lib.esc_motor import ESCMotorHandler
from lib.led import LEDHandler
from lib.message import IncomingMessage, OutgoingMessage
from lib.serial_communication import (
    SerialCommunication,
    SerialCommunicationError,
)
from lib.servo import ServoHandler
from lib.switch import SwitchHandler

# Constants
MOVEMENT = Env.get_movement_mode()
DEBUG = Env.get_debug_mode()
CHALLENGE = Env.get_challenge()
RECEIVING_MESSAGE_TIMEOUT = 1.0

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

    # Loop to handle exceptions and retry initialization
    repeat = True
    while repeat:
        try:
            # Create tasks for initialization
            bno08x_calibrate = create_task(bno08x.calibrate())
            motor_stop = create_task(motor.stop())
            servo_center = create_task(servo.center())

            # Wait for all initialization tasks to complete
            await gather(bno08x_calibrate, motor_stop, servo_center)

            # Wait for the switch to be pressed
            await switch.wait()

            # Set the exit condition to False
            to_exit = False

            # Get start time to compare with the timeout
            start_time = monotonic()

            while not to_exit:
                # Create the update quaternion and receive serial messages tasks
                update_quaternion_task = create_task(
                    bno08x.update_quaternion()
                )
                receive_serial_task = create_task(
                    serial_communication.receive_messages()
                )

                # Wait for the tasks to complete
                results = await gather(
                    update_quaternion_task,
                    receive_serial_task
                    )
                msgs: list[IncomingMessage] = results[1]
                if len(msgs) == 0:
                    # If no messages were received, check if the timeout has been reached
                    if monotonic() - start_time > RECEIVING_MESSAGE_TIMEOUT:
                        raise TimeoutError(
                            "No messages received within the timeout period."
                        )
                else:
                    # Reset the start time if messages are received
                    start_time = monotonic()

                # Algortihm tasks
                tasks = []

                # Process the received messages
                motor_speed = None
                servo_angle = None
                for msg in msgs:
                    if msg == SerialCommunication.HEARTBEAT_MESSAGE:
                        continue

                    if msg == SerialCommunication.STOP_MESSAGE:
                        # Set the exit condition to True
                        to_exit = True

                        # Stop the motor and center the servo
                        tasks.append(create_task(motor.stop()))
                        tasks.append(create_task(servo.center()))

                        # Send a confirmation message to the serial communication
                        tasks.append(
                            create_task(
                                serial_communication.send_confirmation_message()
                            )
                        )
                        break

                    elif msg.category == IncomingCategory.MOTOR_SPEED:
                        # Set the motor speed
                        motor_speed = float(msg.content)

                    elif msg.category == IncomingCategory.SERVO_ANGLE:
                        # Set the servo angle
                        servo_angle = int(msg.content)

                    else:
                        raise SerialCommunicationError(
                            f"Unknown message: {msg.format_to_send_with_error_message()}"
                            )

                # Add the set motor speed task and set servo angle task if the exit flag is not set
                if not to_exit:
                    if motor_speed is not None:
                        tasks.append(
                            create_task(motor.set_speed(motor_speed))
                        )

                    if servo_angle is not None:
                        tasks.append(
                            create_task(servo.set_angle(servo_angle))
                        )

                # Gather the tasks and wait for them to complete
                await gather(*tasks) if tasks else None

            # Stop the serial communication when exiting the loop
            repeat = False
            await serial_communication.stop()

        except Exception as e:
            # Set the speed to 0 and center the servo in case of an exception
            await motor.stop()
            await servo.center()

            # Get the traceback as string
            buf = StringIO()
            print_exception(e, e, e.__traceback__, file=buf)
            msg = OutgoingMessage(OutgoingCategory.ERROR, buf.getvalue())
            serial_communication.send_message_by_chunks(msg)

        # Start the asyncio event loop


run(main())
