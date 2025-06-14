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
DEBUG_MODE = True

# Movement delay
MOVEMENT_DELAY = 0.01

# Speed Values
SPEED_NORMAL = -0.3
SPEED_TURN = -0.25
SPEED_STOP = 0

# Steering servo configuration
TURNING_VALUE = 25

#Difference between the sides is large enough to consider turning
SIDE_DIFFERENCE = 50

#LiDAR Data Configuration
LiDAR_Distances = []

# Desired Gyroscope update rate
GYRO_READ_INTERVAL = 0.05 # 50 ms for 20 Hz updates

#Desired LiDAR update rate
LIDAR_CHECK_DELAY = 0.05

# Start button pins and delay
START_BUTTON_PIN_IN = board.GP14
START_BUTTON_PIN_OUT = board.GP15 
START_BUTTON_DELAY = 0.1

# Distance Thresholds
FRONT_DISTANCE_THRESHOLD = 50
SIDE_DISTANCE_THRESHOLD = 30
TARGET_DISTANCE_STOP = 130

# Steering commands
STEERING_LEFT_COMMAND = -1
STEERING_MIDDLE_COMMAND = 0
STEERING_RIGHT_COMMAND = 1

# Servo pins and configuration
SERVO_PIN = board.GP18
SERVO_PWM_CONFIGURATION = pwmio.PWMOut(SERVO_PIN, duty_cycle=0, frequency=50)
SERVO_DIRECTION = servo.Servo(SERVO_PWM_CONFIGURATION, actuation_range=180, min_pulse=500, max_pulse=2500)
SERVO_DIRECTION_CENTER = 90
SERVO_SETUP_DELAY = 0.1

# Motor pins and configuration
ESC_MOTOR_PIN = board.GP19
ESC_PWM_Configuration = pwmio.PWMOut(ESC_MOTOR_PIN, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)
ESC_SETUP_DELAY = 0.5

# Motor commands
MOTOR_FORWARD = 1
MOTOR_BACKWARD = -1

# ---------- VARIABLES ----------

# Gyroscope state and turn counter (initialized to avoid issues)
last_raw_yaw = None
yaw_deg = 0.0
turns = 0
last_segment_count = 0
initial_yaw = None

# Start button
"""
start_button_in = digitalio.DigitalInOut(START_BUTTON_PIN_IN)
start_button_out = digitalio.DigitalInOut(START_BUTTON_PIN_OUT)
"""

# ---------- SETUP ----------

def setup():
    global bno, initial_yaw
    
    SERVO_DIRECTION.angle = SERVO_DIRECTION_CENTER 
    
    if DEBUG_MODE: 
        print("Arming ESC...")
    ESC.throttle = ROBOT_SPEED_STOP # Set throttle to minimum
    time.sleep(ESC_SETUP_DELAY) # Give ESC time to recognize minimum
    
    ESC.throttle = -ROBOT_SPEED_NORMAL # Send throttle to maximum
    time.sleep(ESC_SETUP_DELAY) # Give ESC time to recognize maximum
    
    ESC.throttle = ROBOT_SPEED_STOP # Set throttle to minimum
    time.sleep(ESC_SETUP_DELAY) # Give ESC time to recognize minimum

    ESC.throttle = ROBOT_SPEED_NORMAL # Return throttle to minimum/stop
    time.sleep(ESC_SETUP_DELAY) # Give ESC time to arm
    
    # Set throttle to minimum
    ESC.throttle = ROBOT_SPEED_STOP
    time.sleep(SERVO_SETUP_DELAY)

    # Initialize start button (SCRAPPED)
    """
    start_button_out.direction = digitalio.Direction.OUTPUT
    start_button_out.value = True
    start_button_in.direction = digitalio.Direction.INPUT
    time.sleep(2)
    if DEBUG_MODE:
        print("Start button value: " + str(start_button_in.value))
    """
    
    try:
        bno = BNO08X_I2C(I2C_BUS, address=0x4B) # Normally you shouldn't have the need to force and I2C address, but in our case we had to
        if DEBUG_MODE:
            print("Gyroscope started correctly.")
    except Exception as e:
        if DEBUG_MODE:
            print(f"ERROR, Gyro failed to start: {e}.")
        raise e
    
    # Don't forget to enable these features
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
            
    time.sleep(1)
    
    #Gathering multiple samples to fix errors
    N = 20
    for _ in range(N):
        quat = bno.quaternion
        time.sleep(0.05)
        
    #Saving the orientation, this makesthe turns variables much smoother to handle
    quat = bno.quaternion
    _, _, initial_yaw_val = quaternion_to_euler_degrees(*quat)
    initial_yaw = initial_yaw_val
    if DEBUG_MODE:
        print(f"Initial yaw captured: {initial_yaw:.2f} degrees")
    
    if DEBUG_MODE:
        print("Started successful")

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
            if DEBUG_MODE:
                print(f"ERROR reading gyro/quaternion: {e}")

        await asyncio.sleep(GYRO_READ_INTERVAL) # Ensures 50ms update rate
        
# ---------- Distance Reading Function ----------

#Just read the average of 10 degrees from each direction
async def lidar_processing():
    LiDAR_Distances = []
    for distance in LiDAR_Distances:
        try:
        except Error as e:
            print("Failed to gather LiDAR Distances, Error: {e}")
            return
    await asyncio.sleep(LIDAR_CHECK_DELAY)
    
# ---------- Movement Functions ----------

def set_robot_speed(speed_throttle):
    # speed_throttle must be a value between -1.0 and 1.0
    ESC.throttle = speed_throttle
    #ESC.angle = ESC_CENTER + speed_throttle

def set_steering_angle(angle):
    # angle must be a value between 0 and 180
    SERVO_DIRECTION.angle = max(0, min(180, angle)) # Clamp angle to valid range

def stop_robot(): # Renamed from 'stop' for consistency
    set_steering_angle(SERVO_DIRECTION_CENTER)
    set_robot_speed(ROBOT_SPEED_STOP) # Use ROBOT_SPEED_STOP

# ---------- Main Robot Control Loop ----------
async def main_robot_loop():  

    steering_command = STEERING_MIDDLE_COMMAND
    motor_command = MOTOR_FORWARD
    going_backward = False
    went_backward = False
    initial_turns = 0
    
    # New variable to track the previous 'turns' count for centering logic
    last_known_turns = 0 

    setup()

    """
    while not start_button_in.value:
        if DEBUG_MODE:
            print("Waiting for start button press...")
        await asyncio.sleep(START_BUTTON_DELAY)
    print("Button press detected, starting program now")
    """
    
    # Start the gyroscope reading as a separate background task
    asyncio.create_task(gyro_reading())
    
    #Start reading the LiDAR data as a separate background task
    asyncio.create_task(lidar_processing())
    
    # Give the gyro task a moment to update 'turns' before initializing last_known_turns
    await asyncio.sleep(GYRO_READ_INTERVAL * 2)
    
    global turns # Ensure we can access the global 'turns'
    last_known_turns = turns # Initialize with the current global turns value

    while True:

        # --- Check for Gyro Turn and Center Servo Immediately ---
        if turns != last_known_turns:
            if DEBUG_MODE:
                print(f"**Turn detected: {turns} (before {last_known_turns}) - Centering Servo**")
            set_steering_angle(STEERING_SERVO_CENTER)
            steering_command = STEERING_MIDDLE_COMMAND  # Override command to center for this cycle
            last_known_turns = turns  # Update for the next check

        # --- Overall Mission Completion Check ---
        if abs(turns) == 12:
            if MOVEMENT_MODE:
                motor_command = MOTOR_FORWARD
                steering_command = STEERING_MIDDLE_COMMAND
                if avg_front_dist<=TARGET_DISTANCE_STOP:
                    set_robot_speed(SPEED_STOP)
                    steering_command = STEERING_MIDDLE_COMMAND
            if DEBUG_MODE:
                print("Done 12 turns, stopping now")
            return

        # --- Navigation Logic ---
        if avg_front_dist >= TARGET_FRONT_THRESHOLD:
            motor_command = MOTOR_FORWARD
            steering_command = STEERING_MIDDLE_COMMAND
            
        elif avg_right_dist >= (avg_left_dist + SIDE_DIFFERENCE):
            motor_command = MOTOR_FORWARD
            steering_command = STEERING_RIGHT_COMMAND
            
        elif avg_left_dist >= (avg_right_dist + SIDE_DIFFERENCE):
            motor_command = MOTOR_FORWARD
            steering_command = STEERING_LEFT_COMMAND

        if MOVEMENT_MODE:
            if steering_command == STEERING_MIDDLE_COMMAND:
                set_robot_speed(SPEED_NORMAL * motor_command)
                set_steering_angle(STEERING_SERVO_CENTER)  # Ensure it's centered if command is middle
            else:
                set_robot_speed(SPEED_TURN * motor_command)
                set_steering_angle(STEERING_SERVO_CENTER - steering_command * TURNING_VALUE)

        if DEBUG_MODE:
            print(f"""Turns: {turns}
Distances: {LiDAR_Distances}
Accumulated Angle Z: {yaw_deg:.2f}°
Motor Direction: {"Going forward" if motor_command == MOTOR_FORWARD else "Going backward"}
Motor Speed: {str(SPEED_NORMAL * motor_command)}
Servo Angle: {STEERING_SERVO.angle:.2f}°
{"-" * 40}
""")
        await asyncio.sleep(MOVEMENT_DELAY)


# Start the asyncio event loop
asyncio.run(main_robot_loop())