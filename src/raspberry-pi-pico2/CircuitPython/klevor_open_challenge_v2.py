import board
import pwmio
import busio
import math
import time
import adafruit_vl53l0x
import digitalio
from adafruit_motor import servo
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)
import asyncio

# ---------- CONSTANTS ----------

# ToF sensors I2C bus
I2C_BUS0 = busio.I2C(board.GP1, board.GP0) 

# Gyroscope I2C bus
I2C_BUS1 = busio.I2C(board.GP27, board.GP26) # Used for Gyroscope

# General configuration
MOVEMENT_MODE = True
DEBUG_MODE = False

# Movement delay
MOVEMENT_DELAY = 0.05

# Speed Values
ROBOT_SPEED_FORWARD_NORMAL = 0.3
ROBOT_SPEED_TURN = 0.2
ROBOT_SPEED_STOP = 0

# Steering servo configuration
TURNING_VALUE = 30 

# ToF Sensors pins and configuration
FRONT_SENSOR_XSHUT_PIN = board.GP5
DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN = board.GP4
DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN = board.GP22
LEFT_MIDDLE_SENSOR_XSHUT_PIN = board.GP7
RIGHT_MIDDLE_SENSOR_XSHUT_PIN = board.GP28
LEFT_REAR_SENSOR_XSHUT_PIN = board.GP12
RIGHT_REAR_SENSOR_XSHUT_PIN = board.GP16
BACK_SENSOR_XSHUT_PIN = board.GP17
TOF_SENSORS_XSHUT_PINS = [FRONT_SENSOR_XSHUT_PIN, DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN, DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN,
              LEFT_MIDDLE_SENSOR_XSHUT_PIN, RIGHT_MIDDLE_SENSOR_XSHUT_PIN, LEFT_REAR_SENSOR_XSHUT_PIN,
              RIGHT_REAR_SENSOR_XSHUT_PIN, BACK_SENSOR_XSHUT_PIN]
TOF_FRONT_SENSOR = 0
TOF_LEFT_MIDDLE_SENSOR = 3
TOF_RIGHT_MIDDLE_SENSOR = 4
TOF_BACK_MIDDLE_SENSOR = 7
TOF_SENSORS_NEW_I2C_ADDRESSES = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37]
TOF_SENSOR_DELAY=0.1
TOF_SENSOR_SHORT_DELAY=0.05

# Start button pins and delay
START_BUTTON_PIN_IN = board.GP14
START_BUTTON_PIN_OUT = board.GP15 
START_BUTTON_DELAY = 0.1

# Distance Thresholds
TARGET_DISTANCE_FORWARD = 80 # When the front sensor distance measured is lower than this, the robot should be starting to approach a turning section
SENSOR_DIFFERENCE_SIDEWAYS = 80 # One of the side sensors detects a distance lower than this value, it is usually compared to another sensor to confirm the distance
TOO_FAR_SIDEWAYS = 200 # This value is pretty much explained above

# Steering commands
STEERING_LEFT_COMMAND = -1
STEERING_MIDDLE_COMMAND = 0
STEERING_RIGHT_COMMAND = 1

# Servo pins and configuration
SERVO_PIN = board.GP20
SERVO_PWM_CONFIGURATION = pwmio.PWMOut(SERVO_PIN, duty_cycle=0, frequency=50)
SERVO_DIRECTION = servo.Servo(SERVO_PWM_CONFIGURATION, actuation_range=180, min_pulse=500, max_pulse=2500)
SERVO_DIRECTION_CENTER = 82
SERVO_DIRECTION.angle = SERVO_DIRECTION_CENTER #This angle actually takes our steering to go forward

# Motor pins and configuration
ESC_MOTOR_PIN = board.GP21
ESC_PWM_Configuration = pwmio.PWMOut(ESC_MOTOR_PIN, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)

# ---------- VARIABLES ----------

# Gyroscope state and turn counter (initialized to avoid issues)
bno = None
yaw_deg = 0.0 
roll_deg = 0.0
pitch_deg = 0.0
last_raw_yaw = None # Stores the raw yaw from previous reading for unwrapping
turns = 0 #Counts each time the robot successfully does a 90-degree turn
last_segment_count = 0 # Helper for counting turns

# List of DigitalInOut objects for XSHUT pins and ToF sensors
vl53l0x_xshut = []
vl53l0x_sensors = []

# Start button
start_button_in = None
start_button_out = None

# ToF sensors measures
tof_sensors_measures = []

# ---------- SETUP ----------

def setup():
    # Initialize Start button
    start_button_out = digitalio.DigitalOut(START_BUTTON_PIN_OUT)
    start_button_in = digitalio.DigitalOut(START_BUTTON_PIN_IN)
    start_button_out.direction = digitalio.Direction.OUTPUT
    start_button_in.direction = digitalio.Direction.IN
    
    try:
        bno = BNO08X_I2C(I2C_BUS1, address=0x4B) # Normally you don't need to force and I2C address, but in our case we had to
        if DEBUG_MODE:
            print("Gyroscope started correctly.")
    except Exception as e:
        if DEBUG_MODE:
            print(f"ERROR, Gyro failed to start: {e}.")
        raise e
    
    # Don't forget to enable these features
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
    
    # Initialize VL53L0X XSHUT pins list here
    if DEBUG_MODE:
        print("Initializing XSHUT pins...")
    for pin_obj in TOF_SENSORS_XSHUT_PINS:
        xshut = digitalio.DigitalInOut(pin_obj)
        xshut.direction = digitalio.Direction.OUTPUT
        xshut.value = False # Keep all sensors off initially
        vl53l0x_xshut.append(xshut)
    
    # Small synchronous pause to ensure all sensors are off
    time.sleep(TOF_SENSOR_DELAY) 
    
    if DEBUG_MODE:
        print("Configuring each ToF Sensor...")
    for i, xshut in enumerate(vl53l0x_xshut):
        if DEBUG_MODE:
            print(f"Activating ToF Sensor {i} and re-addressing...")
        xshut.value = True # Activate the current sensor (pull XSHUT high)
        time.sleep(TOF_SENSOR_DELAY) # Short pause for sensor power-up
    
        try:
            # Initialize the sensor, should be at 0x29
            sensor = adafruit_vl53l0x.VL53L0X(I2C_BUS0)
            
            # Change the I2C address of the current sensor to a new unique address
            sensor.set_address(TOF_SENSORS_NEW_I2C_ADDRESSES[i])
            vl53l0x_sensors.append(sensor)
    
            if DEBUG_MODE:
                print(f"Sensor {i} successfully re-addressed to {hex(TOF_SENSORS_NEW_I2C_ADDRESSES[i])} and ACTIVE.")
            
            time.sleep(TOF_SENSOR_SHORT_DELAY) # Small synchronous pause before activating next sensor
        except ValueError as e:
            if DEBUG_MODE:
                print(f"ERROR: No VL53L0X device found for Sensor {i} at address 0x29.")
                print(f"Detailed Error: {e}")
            break # Exit the loop if a sensor fails to initialize
    
    if len(vl53l0x_sensors) != len(TOF_SENSORS_XSHUT_PINS):
        if DEBUG_MODE:
            print("Error: At least one ToF sensor faield to initialize")
        while True:
            time.sleep(1)
    
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

# Gyroscope Reading Function 
async def gyro_reading():
    global roll_deg, pitch_deg, yaw_deg, last_raw_yaw, turns, last_segment_count

    try:
        quat_x, quat_y, quat_z, quat_w = bno.quaternion
        # raw_yaw_deg will be between -180 and 180 from the quaternion_to_euler_degrees function
        roll_deg, pitch_deg, raw_yaw_deg = quaternion_to_euler_degrees(quat_x, quat_y, quat_z, quat_w)

        if last_raw_yaw is None:
            # Initialize continuous yaw_deg and last_raw_yaw on the first read
            yaw_deg = raw_yaw_deg 
            last_raw_yaw = raw_yaw_deg
            last_segment_count = int(yaw_deg / 90) # Initialize segment count based on continuous yaw
        else:
            # 1. Calculate the change in raw yaw, handling the -180/180 wrap-around
            # This is essential for a truly continuous (unwrapped) yaw
            delta_raw_yaw = raw_yaw_deg - last_raw_yaw
            if delta_raw_yaw > 180:
                delta_raw_yaw -= 360
            elif delta_raw_yaw < -180:
                delta_raw_yaw += 360

            # 2. Add the adjusted delta to the continuous yaw_deg
            yaw_deg += delta_raw_yaw

            # 3. Update 'turns' based on crossing 90-degree boundaries in the continuous yaw_deg
            # This ensures it increments for both directions and only once per 90-degree segment crossing.
            current_segment_count = int(yaw_deg / 90) # Get the current 90-degree segment (e.g., 0, 1, -1, -2)

            if current_segment_count != last_segment_count:
                # Increment 'turns' by the absolute number of 90-degree segments crossed
                turns += abs(current_segment_count - last_segment_count)
                if DEBUG_MODE:
                    print(f"CRUCE: Segmento Anterior={last_segment_count}, Actual={current_segment_count}. Turns={turns}")

            # 4. Update last_raw_yaw and last_segment_count for the next iteration
            last_raw_yaw = raw_yaw_deg
            last_segment_count = current_segment_count

    except Exception as e:
        if DEBUG_MODE:
            print(f"ERROR reading gyro/quaternion: {e}")
    
    await asyncio.sleep(0) # Yield control to other tasks, non-blocking

# ---------- Distance Reading Function ----------
async def read_multiple_tof_sensors():    
    # Iterate over the 'sensors' list which only contains successfully initialized sensors
    for i, sensor in enumerate(vl53l0x_sensors): 
        try:
            distance_mm = sensor.range
            if distance_mm is None or distance_mm >= 3000 or distance_mm < 0: # Handle None or invalid values
                distance_cm = float('inf')
            else:
                distance_cm = distance_mm / 10 # Convert to centimeters
            tof_sensors_measures[i] = distance_cm

        except Exception as e:
            if DEBUG_MODE:
                print(f"Error al leer ToF sensor {i}: {e}") # Specific error message for ToF

# ---------- Movement Functions ----------

def set_robot_speed(speed_throttle):
    # speed_throttle must be a value between -1.0 and 1.0
    ESC.throttle = speed_throttle

def set_steering_angle(angle):
    # angle must be a value between 0 and 180
    SERVO_DIRECTION.angle = max(0, min(180, angle)) # Clamp angle to valid range

def stop_robot(): # Renamed from 'stop' for consistency
    set_steering_angle(SERVO_DIRECTION_CENTER)
    set_robot_speed(ROBOT_SPEED_STOP) # Use ROBOT_SPEED_STOP

# ---------- Main Robot Control Loop (ASYNC) ----------
async def main_robot_loop(): # Renamed from Main_Loop for consistency and best practice
    # Set the initial steering command as middle
    steering_command = STEERING_MIDDLE_COMMAND
    
    # Call the setup function
    setup()

    while not start_button_in.value:
        if DEBUG_MODE:
            print("Waiting for start button press...")
        await asyncio.sleep(START_BUTTON_DELAY)
    print("Button press detected, starting program now")

    while True:
        # Read all the data asynchronously
        await gyro_reading() 
        await read_multiple_tof_sensors()
        front_dist = tof_sensors_measures[TOF_FRONT_SENSOR]
        right_middle_dist = tof_sensors_measures[TOF_RIGHT_MIDDLE_SENSOR]
        left_middle_dist = tof_sensors_measures[TOF_LEFT_MIDDLE_SENSOR]
        back_dist = tof_sensors_measures[TOF_BACK_MIDDLE_SENSOR]

        if front_dist<=TARGET_DISTANCE_FORWARD and right_middle_dist >= (left_middle_dist + SENSOR_DIFFERENCE_SIDEWAYS):
            steering_command = STEERING_RIGHT_COMMAND
            if MOVEMENT_MODE:
                set_robot_speed(ROBOT_SPEED_TURN)
                set_steering_angle(SERVO_DIRECTION_CENTER + TURNING_VALUE)

        elif front_dist<=TARGET_DISTANCE_FORWARD and left_middle_dist >= (right_middle_dist + SENSOR_DIFFERENCE_SIDEWAYS) and steering_command>=0: #i need to organize what its gonna make them choose to go left
            steering_command = STEERING_LEFT_COMMAND
            if MOVEMENT_MODE:
                set_robot_speed(ROBOT_SPEED_TURN)
                set_steering_angle(SERVO_DIRECTION_CENTER - TURNING_VALUE)

        else:
            steering_command = STEERING_MIDDLE_COMMAND
            if MOVEMENT_MODE:
                set_robot_speed(ROBOT_SPEED_FORWARD_NORMAL)
                set_steering_angle(SERVO_DIRECTION_CENTER)

        if turns >= 12: # If robot has completed 12 turns
            if MOVEMENT_MODE:
                if front_dist >= 100 and back_dist >= 100:
                    stop_robot()
            if DEBUG_MODE:
                print("Done 12 turns, stopping now")

        if DEBUG_MODE:
            distances_str = ", ".join([f"ToF{i}: {d:.1f}cm" for i, d in enumerate(tof_sensors_measures)])
            print(f"Distancias ToF: [{distances_str}]")
            # yaw_deg is now the continuously unwrapped angle
            print(f"Angulo Z acumulado: {yaw_deg:.2f}°") 
            print(f"Cruces hechos (turns): {turns}")
            print(f"Angulo de dirección del servo: {SERVO_DIRECTION.angle:.2f}°")
            # Additional debug print for current movement state

        await asyncio.sleep(MOVEMENT_DELAY)

# Start the asyncio event loop
asyncio.run(main_robot_loop())