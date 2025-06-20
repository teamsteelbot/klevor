import board
import busio
import digitalio
import time
from lib.bno08x import *
from lib.esc_motor import *
from lib.serial_communication import *
from lib.servo import *
from lib.switch import *
from lib.wifi import *
import asyncio

# ---------- CONSTANTS ----------

# Gyroscope I2C Bus
I2C_BUS = busio.I2C(board.GP1, board.GP0)

#Motor Pin
ESC_MOTOR_PIN = board.GP2

#Servo Pin
SERVO_PIN = board.GP13

#Switch Pin
SWITCH_PIN = board.GP11

# General configuration
MOVEMENT_MODE = True
DEBUG = False

# Movement delay
MOVEMENT_DELAY = 0.1

# Speed Values
SPEED_NORMAL = -0.5
SPEED_TURN = -0.35
SPEED_STOP = 0

# Steering servo configuration
TURNING_VALUE = 25
TURNING_DELAY = 0.1

#Switch Delay
SWITCH_DELAY = 0.01

#Gyroscope Reading Interval
GYRO_READ_INTERVAL = 0.02

# Parking delay
PARKING_DELAY = 0.1

# Turn on delay
TURN_ON_DELAY = 2

# Sent start message delay
SENT_START_MESSAGE_DELAY = 0.5

#Serial communication headers
USB_CDC_HEADER_RPLIDAR = "rplidar"
USB_CDC_HEADER_STATUS = "status"
USB_CDC_HEADER_SEPARATOR = ":"
USB_CDC_RPLIDAR_CONTENT_SEPARATOR = ","

#LED Pin
led_pin = digitalio.DigitalInOut(board.LED)
led_pin.direction = digitalio.Direction.OUTPUT

# Start and stop message
START_MESSAGE = f"{USB_CDC_HEADER_STATUS}{USB_CDC_HEADER_SEPARATOR}on"
STOP_MESSAGE = f"{USB_CDC_HEADER_STATUS}{USB_CDC_HEADER_SEPARATOR}off"

# ---------- SETUP ----------

servo: ServoHandler = None
motor: ESCMotorHandler = None
gyroscope: BNO08XHandler = None
serial_handler: SerialCommunication = None
switch: SwitchHandler = None

def setup():

    servo = ServoHandler(servo_pin=SERVO_PIN)
    motor = ESCMotorHandler(motor_pin=ESC_MOTOR_PIN)
    gyroscope = BNO08XHandler(BNO08X_I2C=I2C_BUS)
    serial_handler = SerialCommunication(console_port_enabled=True, data_port_enabled=True, toggle_led_on_receive=True)
    switch = SwitchHandler(switch_pin=SWITCH_PIN)

    # Last motor speed and servo angle
    last_motor_speed = SPEED_STOP
    last_servo_angle = servo.SERVO_CENTER_ANGLE
    
    servo.angle = servo.SERVO_CENTER_ANGLE 

    # Gathering multiple samples to fix errors
    N = 20
    for _ in range(N):
        quat = BNO08XHandler.__read_quaternion
        time.sleep(0.05)
        
    # Saving the orientation, this makes the turns variables much smoother to handle
    quat = BNO08XHandler.__read_quaternion
    _, _, initial_yaw_val = BNO08XHandler.__quaternion_to_euler_degrees(*quat)
    gyroscope.initial_yaw = initial_yaw_val
    
# ---------- Movement Functions ----------

def set_robot_speed(speed_throttle):
    """
    Set the speed of the robot by adjusting the ESC throttle.
    Args:
        speed_throttle (float): The desired speed throttle value, must be between -1.0 and 1.0.
    """
    global last_motor_speed

    if last_motor_speed == speed_throttle:
        return
    
    motor.speed = speed_throttle
    last_motor_speed = speed_throttle
    serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:motor,{speed_throttle}")

def set_steering_angle(angle):
    """
    Set the steering angle of the robot.
    Args:
        angle (int): The desired steering angle in degrees, must be between 0 and 180.
    """
    global last_servo_angle

    if last_servo_angle == angle:
        return
    
    servo.angle = max(0, min(180, angle)) # Clamp angle to valid range
    last_servo_angle = angle
    serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:servo,{angle}")

def stop_robot(): # Renamed from 'stop' for consistency
    set_steering_angle(servo.SERVO_CENTER_ANGLE)
    set_robot_speed(SPEED_STOP)

async def gyro_update():
    gyroscope.update_quaternion
    await asyncio.sleep (GYRO_READ_INTERVAL)

# ---------- Main Robot Control Loop ----------

async def main_robot_loop():  

    # Initialize the robot state
    setup()

    # Turn on built-in LED to show that it's ready
    if DEBUG:
        led_pin.value = True
        time.sleep(TURN_ON_DELAY)
        led_pin.value = False
        time.sleep(TURN_ON_DELAY)
        
    # Wait for the switch to be pressed to start the robot
    while switch.value:
        time.sleep(SWITCH_DELAY)  # Pequeña pausa para debouncing y eficiencia (ajusta si es necesario)

    # Send start message
    serial_handler.send_message(START_MESSAGE)

    #  Turn on built-in LED two times to show that the start message has been sent
    if DEBUG:
        for i in range(2):
            led_pin.value = True
            time.sleep(SENT_START_MESSAGE_DELAY)
            led_pin.value = False
            time.sleep(SENT_START_MESSAGE_DELAY)
    
    # Create a receiving message handler task
    #asyncio.create_task(receive_message_handler())

    # Start the gyroscope reading as a separate background task
    #asyncio.create_task(gyro_reading())

    # Initialize with the current global turns value
    last_known_turns = gyroscope.turns 
    turning = False
    if DEBUG:
        serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:starting main algorithm")

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
                time.sleep(TURNING_DELAY)  
                continue

        """       
        if DEBUG:
            serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:avg_front_dist,{avg_front_dist}")
            serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:avg_right_dist,{avg_right_dist}")
            serial_handler.send_message(f"{USB_CDC_HEADER_STATUS}:avg_left_dist,{avg_left_dist}")

        # Overall Mission Completion Check
        if abs(gyroscope.turns) == 12:
            if MOVEMENT_MODE:
                set_robot_speed(SPEED_NORMAL)
                set_steering_angle(servo.SERVO_CENTER_ANGLE)

                while True:
                    if avg_front_dist > TARGET_DISTANCE_STOP_START and avg_front_dist < TARGET_DISTANCE_STOP_END:
                        set_robot_speed(SPEED_STOP)
                        serial_handler.send_message(STOP_MESSAGE)

                    time.sleep(PARKING_DELAY)
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

        time.sleep(MOVEMENT_DELAY)
        """

# Start the asyncio event loop
asyncio.run(main_robot_loop())