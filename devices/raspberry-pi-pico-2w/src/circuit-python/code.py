import board
import busio
import digitalio
from time import sleep
import asyncio

from lib.bno08x import BNO08XHandler
from lib.env import Env
from lib.esc_motor import ESCMotorHandler
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
serial_communication: SerialCommunication = SerialCommunication(console_port_enabled=True, data_port_enabled=True, toggle_led_on_receive=True)
servo: ServoHandler = ServoHandler(servo_pin=SERVO_PIN, serial_communication=serial_communication)
motor: ESCMotorHandler = ESCMotorHandler(motor_pin=ESC_MOTOR_PIN, serial_communication=serial_communication)
bno08x: BNO08XHandler = BNO08XHandler(i2c=I2C_BUS)
switch: SwitchHandler = SwitchHandler(switch_pin=SWITCH_PIN)

# ---------- Main Robot Control Loop ----------

async def main_robot_loop():  

    # Initialize the robot state
    setup()

    # Turn on built-in LED to show that it's ready
    if DEBUG:
        led_pin.value = True
        sleep(TURN_ON_DELAY)
        led_pin.value = False
        sleep(TURN_ON_DELAY)
        
    # Wait for the switch to be pressed to start the robot
    while switch.value:
        sleep(SWITCH_DELAY)  # Pequeña pausa para debouncing y eficiencia (ajusta si es necesario)

    # Send start message
    serial_communication.send_message(START_MESSAGE)

    #  Turn on built-in LED two times to show that the start message has been sent
    if DEBUG:
        for i in range(2):
            led_pin.value = True
            sleep(SENT_START_MESSAGE_DELAY)
            led_pin.value = False
            sleep(SENT_START_MESSAGE_DELAY)
    
    # Create a receiving message handler task
    #asyncio.create_task(receive_message_handler())

    # Start the gyroscope reading as a separate background task
    #asyncio.create_task(gyro_reading())

    # Initialize with the current global turns value
    last_known_turns = gyroscope.turns 
    turning = False
    if DEBUG:
        serial_communication.send_message(f"{USB_CDC_HEADER_STATUS}:starting main algorithm")

    while True:
        # Update gyro
        gyro_update()
        
        # Check for Gyro Turn and Center Servo Immediately
        if turning:
            if gyroscope.turns != last_known_turns:
                set_steering_angle(servo.SERVO_CENTER_ANGLE)

                # Update for the next check
                last_known_turns = gyroscope.turns  
                turning = False
            else:
                # Wait a bit before checking again
                sleep(TURNING_DELAY)  
                continue

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
asyncio.run(main_robot_loop())