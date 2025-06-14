import board
import usb_cdc
import pwmio
import busio
import math
import time
import digitalio
import sys
from adafruit_motor import servo
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)
import asyncio

# ---------- CONSTANTS ----------

# Gyroscope I2C Bus
I2C_BUS = busio.I2C(board.GP1, board.GP0) 

# General configuration
MOVEMENT_MODE = True
DEBUG = True

# Movement delay
MOVEMENT_DELAY = 0.2

# Speed Values
SPEED_NORMAL = -0.3
SPEED_TURN = -0.25
SPEED_STOP = 0

# Steering servo configuration
TURNING_VALUE = 25
TURNING_DELAY = 0.1

# Parking delay
PARKING_DELAY = 0.1

# Difference between the sides is large enough to consider turning
SIDE_DIFFERENCE_PERCENTAGE = 0.2

# USB CDC headers
USB_CDC_HEADER_RPLIDAR = "rplidar"
USB_CDC_HEADER_SEPARATOR = ":"
USB_CDC_RPLIDAR_CONTENT_SEPARATOR = ","

# RPLIDAR Data Configuration
RPLIDAR_MAX_DISTANCE = 3000
RPLIDAR_DISTANCE_TOGGLE_LED_DELAY = 0.0015

# Desired Gyroscope update rate
GYRO_READ_INTERVAL = 0.05 # 50 ms for 20 Hz updates

# Switch configuration
SWITCH_PIN = board.GP11
SWITCH_DELAY = 0.1

# Distance Thresholds
FRONT_DISTANCE_THRESHOLD = 500
SIDE_DISTANCE_THRESHOLD = 1500
TARGET_DISTANCE_STOP_START = 2000
TARGET_DISTANCE_STOP_END = 1000

# Servo pins and configuration
SERVO_PIN = board.GP13
SERVO_PWM_CONFIGURATION = pwmio.PWMOut(SERVO_PIN, duty_cycle=0, frequency=50)
STEERING_SERVO = servo.Servo(SERVO_PWM_CONFIGURATION, actuation_range=180, min_pulse=500, max_pulse=2500)
STEERING_SERVO_CENTER = 90
SERVO_SETUP_DELAY = 0.1

# Motor pins and configuration
ESC_MOTOR_PIN = board.GP2
ESC_PWM_Configuration = pwmio.PWMOut(ESC_MOTOR_PIN, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)
ESC_SETUP_DELAY = 0.2

# Start and stop message
START_MESSAGE = "status:on"
STOP_MESSAGE = "status:off"

# ---------- VARIABLES ----------

# Gyroscope state and turn counter (initialized to avoid issues)
last_raw_yaw = None
yaw_deg = 0.0
turns = 0
last_segment_count = 0
initial_yaw = None

# Data port 
data_port = usb_cdc.data
data_port.reset_input_buffer()
data_port.reset_output_buffer()

# RPLIDAR distances
RPLIDAR_DISTANCES = [RPLIDAR_MAX_DISTANCE for i in range(360)]

# ---------- USB CDC Setup ----------

def receive_message() -> str|None:
    """
    Receive a message from the USB CDC data stream.
    Returns:
        str|None: The received message as a string, or None if no message is available.
    """
    if data_port.in_waiting > 0:
        return data_port.readline().strip().decode("utf-8")

async def receive_message_handler():
    """
    Receive messages from the USB CDC data stream in a non-blocking way.
    """
    while True:
        if data_port.in_waiting > 0:
            # Turn on the LED fast to indicate data reception
            if DEBUG:
                led_pin.value = True
                time.sleep(RPLIDAR_DISTANCE_TOGGLE_LED_DELAY)
                led_pin.value = False
                time.sleep(RPLIDAR_DISTANCE_TOGGLE_LED_DELAY)

            # Read the message from the data port
            message = data_port.readline().strip().decode("utf-8")
            parts = message.split(USB_CDC_HEADER_SEPARATOR)

            # Check if it's a RPLIDAR message
            if len(parts) < 2:
                continue

            if parts[0] == USB_CDC_HEADER_RPLIDAR:
                rplidar_content = parts[1].split(USB_CDC_RPLIDAR_CONTENT_SEPARATOR)
                if len(rplidar_content) < 3:
                    continue
                
                # Parse the RPLIDAR content
                angle = int(float(rplidar_content[0]))
                distance = int(float(rplidar_content[1]))
                quality = int(rplidar_content[2])

                # Check the distance and quality
                if quality > 0 and distance < RPLIDAR_MAX_DISTANCE and 0 <= angle < 360:
                    RPLIDAR_DISTANCES[angle] = distance

def send_message(message: str):
    """
    Send a message to the USB CDC data stream.
    
    Args:
        message (str): The message to send.
    """
    try:
        data_port.write((message + "\n").encode("utf-8"))
    except Exception as e:
        pass

def wait_for_confirmation(message_to_compare: str):
    while True:
        message_received = receive_message()
        if message_received and message_received == message_to_compare:
            break

# ---------- SETUP ----------

def setup():
    global bno, initial_yaw, led_pin, switch_pin
    
    STEERING_SERVO.angle = STEERING_SERVO_CENTER 

    # Initialize the ESC
    ESC.throttle = SPEED_STOP
    time.sleep(ESC_SETUP_DELAY)

    # Start button
    switch_pin = digitalio.DigitalInOut(SWITCH_PIN)
    switch_pin.direction = digitalio.Direction.INPUT
    switch_pin.pull = digitalio.Pull.UP

    # LED pin
    led_pin = digitalio.DigitalInOut(board.LED)
    led_pin.direction = digitalio.Direction.OUTPUT

    try:
        bno = BNO08X_I2C(I2C_BUS, address=0x4B) # Normally you shouldn't have the need to force and I2C address, but in our case we had to
   
    except Exception as e:
        raise e
    
    # Don't forget to enable these features
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
    time.sleep(1)
    
    # Gathering multiple samples to fix errors
    N = 20
    for _ in range(N):
        quat = bno.quaternion
        time.sleep(0.05)
        
    # Saving the orientation, this makesthe turns variables much smoother to handle
    quat = bno.quaternion
    _, _, initial_yaw_val = quaternion_to_euler_degrees(*quat)
    initial_yaw = initial_yaw_val

# ---------- SENSOR FUNCTIONS ----------

# This function receives the 4 components of the quaternion and calculates the orientation
def quaternion_to_euler_degrees(x, y, z, w):
    # Roll
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll_rad = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch
    sinp = 2 * (w * y - z * x)
    # Clamp the value to avoid domain errors for asin (should be between -1 and 1)
    pitch_rad = math.asin(min(1, max(-1, sinp))) # Clamp value to avoid domain errors for asin

    # Yaw
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw_rad = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll_rad), math.degrees(pitch_rad), math.degrees(yaw_rad)

# Gyroscope Reading Function (now runs as a background task)
async def gyro_reading():
    global initial_yaw, last_raw_yaw, yaw_deg, turns, last_segment_count
    while True: # Keep reading indefinitely in the background
        try:
            quat_x, quat_y, quat_z, quat_w = bno.quaternion
            roll_deg, pitch_deg, raw_yaw_deg = quaternion_to_euler_degrees(quat_x, quat_y, quat_z, quat_w)

            # Compute relative yaw
            relative_yaw = raw_yaw_deg - initial_yaw
            if relative_yaw > 180:
                relative_yaw -= 360
            elif relative_yaw < -180:
                relative_yaw += 360

            if last_raw_yaw is None:
                yaw_deg = relative_yaw
                last_raw_yaw = relative_yaw
                last_segment_count = int(yaw_deg / 90)
            else:
                delta_raw_yaw = relative_yaw - last_raw_yaw
                if delta_raw_yaw > 180:
                    delta_raw_yaw -= 360
                elif delta_raw_yaw < -180:
                    delta_raw_yaw += 360

                yaw_deg += delta_raw_yaw

                current_segment_count = int(yaw_deg / 90)
                if current_segment_count != last_segment_count:
                    turns += current_segment_count - last_segment_count
                    last_segment_count = current_segment_count

                last_raw_yaw = relative_yaw

        except Exception as e:
            pass

        await asyncio.sleep(GYRO_READ_INTERVAL) # Ensures 50ms update rate
    
# ---------- Movement Functions ----------

def set_robot_speed(speed_throttle):
    """
    Set the speed of the robot by adjusting the ESC throttle.
    Args:
        speed_throttle (float): The desired speed throttle value, must be between -1.0 and 1.0.
    """
    ESC.throttle = speed_throttle

def set_steering_angle(angle):
    """
    Set the steering angle of the robot.
    Args:
        angle (int): The desired steering angle in degrees, must be between 0 and 180.
    """
    STEERING_SERVO.angle = max(0, min(180, angle)) # Clamp angle to valid range

def stop_robot(): # Renamed from 'stop' for consistency
    set_steering_angle(STEERING_SERVO_CENTER)
    set_robot_speed(SPEED_STOP)

# ---------- Main Robot Control Loop ----------

async def main_robot_loop():  
    global turns 

    # Initialize the robot state
    setup()
    
    # Wait for the switch to be pressed to start the robot
    while not switch_pin.value:
        time.sleep(SWITCH_DELAY)  # Pequeña pausa para debouncing y eficiencia (ajusta si es necesario)

    # Start the gyroscope reading as a separate background task
    asyncio.create_task(gyro_reading())
    
    # Create a receiving message handler task
    asyncio.create_task(receive_message_handler())
    
    # Give the gyro task a moment to update 'turns' before initializing last_known_turns
    await asyncio.sleep(GYRO_READ_INTERVAL * 2)

    # Initialize with the current global turns value
    last_known_turns = turns 
    turning = False

    while True:
        # Check for Gyro Turn and Center Servo Immediately
        if turning:
            if turns != last_known_turns:
                set_steering_angle(STEERING_SERVO_CENTER)

                # Update for the next check
                last_known_turns = turns  
                turning = False
            else:
                # Wait a bit before checking again
                time.sleep(TURNING_DELAY)  
                continue

        # Calculate average distances from RPLIDAR data
        avg_front_dist = (sum(RPLIDAR_DISTANCES[-5:]) + sum(RPLIDAR_DISTANCES[:5])) / 10.0
        avg_left_dist = sum(RPLIDAR_DISTANCES[265:275]) / 10.0
        avg_right_dist = sum(RPLIDAR_DISTANCES[85:95]) / 10.0

        # Overall Mission Completion Check
        if abs(turns) == 12:
            if MOVEMENT_MODE:
                set_robot_speed(SPEED_NORMAL)
                set_steering_angle(STEERING_SERVO_CENTER)

                while True:
                    if avg_front_dist > TARGET_DISTANCE_STOP_START and avg_front_dist < TARGET_DISTANCE_STOP_END:
                        set_robot_speed(SPEED_STOP)
                        send_message(STOP_MESSAGE)

                    time.sleep(PARKING_DELAY)
            return

        # --- Navigation Logic ---
        if avg_front_dist >= FRONT_DISTANCE_THRESHOLD:
            set_robot_speed(SPEED_NORMAL)
            
            if avg_right_dist >= avg_left_dist * (1 + SIDE_DIFFERENCE_PERCENTAGE):
                set_steering_angle(STEERING_SERVO_CENTER - TURNING_VALUE)
                
            elif avg_left_dist >= avg_right_dist * (1 + SIDE_DIFFERENCE_PERCENTAGE):
                set_steering_angle(STEERING_SERVO_CENTER + TURNING_VALUE)
            
            else:
                set_steering_angle(STEERING_SERVO_CENTER)

        else:
            set_robot_speed(SPEED_TURN)
            
            if avg_right_dist >= SIDE_DISTANCE_THRESHOLD:
                set_steering_angle(STEERING_SERVO_CENTER - TURNING_VALUE)
            elif avg_left_dist >= SIDE_DISTANCE_THRESHOLD:
                set_steering_angle(STEERING_SERVO_CENTER + TURNING_VALUE)

        await asyncio.sleep(MOVEMENT_DELAY)

# Start the asyncio event loop
asyncio.run(main_robot_loop())