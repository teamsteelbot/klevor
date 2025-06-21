import board
import busio
import digitalio
from time import sleep
from asyncio import run, create_task, gather

from lib.bno08x import BNO08XHandler
from lib.env import Env
from lib.esc_motor import ESCMotorHandler
from lib.led import LEDHandler
from lib.serial_communication import SerialCommunication
from lib.servo import ServoHandler
from lib.switch import SwitchHandler

# Constants
DEBUG = Env.get_debug_mode()
CHALLENGE = Env.get_challenge()

# Pins
I2C_BUS = busio.I2C(board.GP1, board.GP0)
ESC_MOTOR_PIN = board.GP2
SERVO_PIN = board.GP13
SWITCH_PIN = board.GP11

# Robot's components handlers
led: LEDHandler = LEDHandler(led_pin=board.LED)
serial_communication: SerialCommunication = SerialCommunication(console_port_enabled=True, data_port_enabled=True, led=led)
servo: ServoHandler = ServoHandler(servo_pin=SERVO_PIN, serial_communication=serial_communication)
motor: ESCMotorHandler = ESCMotorHandler(motor_pin=ESC_MOTOR_PIN, serial_communication=serial_communication)
bno08x: BNO08XHandler = BNO08XHandler(i2c=I2C_BUS)
switch: SwitchHandler = SwitchHandler(switch_pin=SWITCH_PIN, serial_communication=serial_communication, led=led)

async def main():
    """
    Main function to initialize the robot and start the main algorithm.
    """
    global bno08x, servo, motor, switch, serial_communication, led

    # Create tasks for initialization
    bno08x_calibrate = create_task(bno08x.calibrate())
    motor_stop = create_task(motor.stop())
    servo_center = create_task(servo.center())
    switch_wait = create_task(switch.wait())

    # Wait for all initialization tasks to complete
    await gather(bno08x_calibrate, motor_stop, servo_center, switch_wait)

    # Set the last known turns to zero
    last_known_turns = 0

    while True:
        # Create the update quaternion and receive serial messages tasks
        update_quaternion_task = create_task(bno08x.update_quaternion())
        receive_serial_task = create_task(serial_communication.receive_message())

        # Wait for the tasks to complete
        await gather(update_quaternion_task, receive_serial_task)

        # Algorithm tasks
        tasks = []

        # Check for the current turn and center the servo if necessary
        if servo.is_turning() and bno08x.turns != last_known_turns:
            tasks.append(create_task(servo.center()))

            # Update for the next check
            last_known_turns = bno08x.turns

        """       
        if DEBUG:
            serial_communication.send_message(f"{USB_CDC_HEADER_STATUS}:avg_front_dist,{avg_front_dist}")
            serial_communication.send_message(f"{USB_CDC_HEADER_STATUS}:avg_right_dist,{avg_right_dist}")
            serial_communication.send_message(f"{USB_CDC_HEADER_STATUS}:avg_left_dist,{avg_left_dist}")

        # Overall Mission Completion Check
        if abs(gyroscope.turns) == 12:
            if MOVEMENT_MODE:
                set_robot_speed(SPEED_NORMAL)
                set_steering_angle(servo.SERVO_CENTER_ANGLE)

                while True:
                    if avg_front_dist > TARGET_DISTANCE_STOP_START and avg_front_dist < TARGET_DISTANCE_STOP_END:
                        set_robot_speed(SPEED_STOP)
                        serial_communication.send_message(STOP_MESSAGE)

                    sleep(PARKING_DELAY)
            return
        
        # --- Navigation Logic ---
        if avg_front_dist >= FRONT_DISTANCE_THRESHOLD:
            set_robot_speed(SPEED_NORMAL)
            
            if avg_right_dist >= avg_left_dist * (1 + SIDE_DIFFERENCE_PERCENTAGE):
                set_steering_angle(servo.SERVO_CENTER_ANGLE - TURNING_VALUE)
                
            elif avg_left_dist >= avg_right_dist * (1 + SIDE_DIFFERENCE_PERCENTAGE):
                set_steering_angle(servo.SERVO_CENTER_ANGLE + TURNING_VALUE)
            
            else:
                set_steering_angle(servo.SERVO_CENTER_ANGLE)

        else:
            set_robot_speed(SPEED_TURN)
            
            if avg_right_dist >= SIDE_DISTANCE_THRESHOLD:
                set_steering_angle(servo.SERVO_CENTER_ANGLE - TURNING_VALUE)
            elif avg_left_dist >= SIDE_DISTANCE_THRESHOLD:
                set_steering_angle(servo.SERVO_CENTER_ANGLE + TURNING_VALUE)

        sleep(MOVEMENT_DELAY)
        """
        sleep(ESCMotorHandler.DELAY)

# Start the asyncio event loop
run(main())