#-----------------------------LIBRARIES----------------------------
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


i2c_bus0 = busio.I2C(board.GP1, board.GP0) # Used for ToF Sensors
i2c_bus1 = busio.I2C(board.GP27, board.GP26) # Used for Gyroscope

#----------------VARIABLES----------------

MOVEMENT_MODE = 1
DEBUG_MODE = 0

#Speed Values
ROBOT_SPEED_FORWARD_NORMAL = -0.3
ROBOT_SPEED_TURN = -0.2 
ROBOT_SPEED_STOP = 0

# Steering servo configuration
STEERING_COMPENSATION = 0 # Factor for yaw-based steering correction (if it does work, might not)
TURNING_VALUE = 30 

#ToF Sensors defining
FRONT_SENSOR_XSHUT_PIN = board.GP5
DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN = board.GP4
DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN = board.GP22
LEFT_MIDDLE_SENSOR_XSHUT_PIN = board.GP7
RIGHT_MIDDLE_SENSOR_XSHUT_PIN = board.GP28
LEFT_REAR_SENSOR_XSHUT_PIN = board.GP12
RIGHT_REAR_SENSOR_XSHUT_PIN = board.GP16
BACK_SENSOR_XSHUT_PIN = board.GP17

# Pin definitions for Servo and Motor
SERVO_PIN = board.GP20
ESC_Motor_Pin = board.GP21

# Pin for the Start Button
START_BUTTON_PIN = board.GP15 

# Global variables for gyroscope state and turn counter (initialized to avoid issues)
yaw_deg = 0.0 
roll_deg = 0.0
pitch_deg = 0.0
last_raw_yaw = None # Stores the raw yaw from previous reading for unwrapping
turns = 0 #Counts each time the robot successfully does a 90-degree turn
last_segment_count = 0 # Helper for counting turns
steering_command = 0 # This variable gets adjusted depending on whether or not the robot needs to go forward, left or right                                                                                                                                          

# Distance Thresholds
TARGET_DISTANCE_FORWARD = 80 # When the front sensor distance measured is lower than this, the robot should be starting to approach a turning section
SENSOR_DIFFERENCE_SIDEWAYS = 80 # One of the side sensors detects a distance lower than this value, it is usually compared to another sensor to confirm the distance
TOO_FAR_SIDEWAYS = 200 # This value is pretty much explained above

#------------------------SETUP--------------------------------

# Initialize Start Button Pin
start_button = digitalio.DigitalInOut(START_BUTTON_PIN)
start_button.direction = digitalio.Direction.INPUT
start_button.pull = digitalio.Pull.UP # Enable internal pull-up resistor

try:
    bno = BNO08X_I2C(i2c_bus1, address=0x4B) # Normally you dont need to force and I2C address, but in our case we had to
    if DEBUG_MODE == 1:
        print("Gyroscope started correctly.")
except Exception as e:
    if DEBUG_MODE == 1:
        print(f"ERROR, Gyro failed to start: {e}.")
    while True: #Stops program in case it starts to fail
        time.sleep(1)

# Don't forget to enable these features
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

# Initialize ToF Sensors (VL53L0X) - using i2c_bus0 as per your current code's wiring
xshut_pins = [FRONT_SENSOR_XSHUT_PIN, DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN, DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN, LEFT_MIDDLE_SENSOR_XSHUT_PIN, RIGHT_MIDDLE_SENSOR_XSHUT_PIN, LEFT_REAR_SENSOR_XSHUT_PIN, RIGHT_REAR_SENSOR_XSHUT_PIN, BACK_SENSOR_XSHUT_PIN]

vl53l0x_xshut = [] # List to store DigitalInOut objects for XSHUT pins
sensors = []       # List to store VL53L0X sensor objects

# New unique I2C addresses for each sensor
new_i2c_addresses = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37]

# ---Initialize vl53l0x_xshut list here ---
if DEBUG_MODE == 1:
    print("Initializing XSHUT pins")
for pin_obj in xshut_pins:
    xshut = digitalio.DigitalInOut(pin_obj)
    xshut.direction = digitalio.Direction.OUTPUT
    xshut.value = False # Keep all sensors off initially
    vl53l0x_xshut.append(xshut)
    
time.sleep(0.1) # Small synchronous pause to ensure all sensors are off

if DEBUG_MODE == 1:
    print("Configurating each ToF Sensor")
for i, xshut_pin in enumerate(vl53l0x_xshut):
    if DEBUG_MODE == 1:
        print(f"--- Activating Sensor {i} and re-addressing ---")
    xshut_pin.value = True # Activate the current sensor (pull XSHUT high)
    time.sleep(0.1) # Short pause for sensor power-up

    try:
        # Initialize the sensor, should be at 0x29
        sensor = adafruit_vl53l0x.VL53L0X(i2c_bus0)
        
        # Change the I2C address of the current sensor to a new unique address
        sensor.set_address(new_i2c_addresses[i])
        sensors.append(sensor)

        if DEBUG_MODE == 1:
            print(f"Sensor {i} successfully re-addressed to {hex(new_i2c_addresses[i])} and ACTIVE.")
        
        time.sleep(0.05) # Small synchronous pause before activating next sensor
    except ValueError as e:
        if DEBUG_MODE == 1:
            print(f"ERROR: No VL53L0X device found for Sensor {i} at address 0x29.")
            print(f"Detailed Error: {e}")
        break # Exit the loop if a sensor fails to initialize

if len(sensors) != len(xshut_pins):
    if DEBUG_MODE == 1:
        print("Error: At least one ToF sensor faield to initialize")
    while True:
        time.sleep(1)

if DEBUG_MODE == 1:
    print("Start successful")

Servo_PWM_Configuration = pwmio.PWMOut(SERVO_PIN, duty_cycle=0, frequency=50)
Direction_Servo = servo.Servo(Servo_PWM_Configuration, actuation_range=180, min_pulse=500, max_pulse=2500)

Direction_Servo.angle = 82 #This angle actually takes our steering to go forward

ESC_PWM_Configuration = pwmio.PWMOut(ESC_Motor_Pin, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)

# ---------- SETUP END ----------

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

# ---------- Gyroscope Reading Function ----------

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
                if DEBUG_MODE == 1:
                    print(f"CRUCE: Segmento Anterior={last_segment_count}, Actual={current_segment_count}. Turns={turns}")

            # 4. Update last_raw_yaw and last_segment_count for the next iteration
            last_raw_yaw = raw_yaw_deg
            last_segment_count = current_segment_count

    except Exception as e:
        if DEBUG_MODE == 1:
            print(f"ERROR reading gyro/quaternion: {e}")
    
    await asyncio.sleep(0) # Yield control to other tasks, non-blocking

# ---------- Distance Reading Function ----------
async def read_multiple_tof_sensors():
    current_distances_cm = []
    # Iterate over the 'sensors' list which only contains successfully initialized sensors
    for i, sensor in enumerate(sensors): 
        try:
            distance_mm = sensor.range
            if distance_mm is None or distance_mm >= 3000 or distance_mm < 0: # Handle None or invalid values
                distance_cm = float('inf')
            else:
                distance_cm = distance_mm / 10 # Convert to centimeters
            current_distances_cm.append(distance_cm)

        except Exception as e:
            if DEBUG_MODE == 1:
                print(f"Error al leer ToF sensor {i}: {e}") # Specific error message for ToF
            current_distances_cm.append(float('inf'))
    await asyncio.sleep(0)
    return current_distances_cm

# ---------- Movement Functions ----------
def set_robot_speed(speed_throttle):
    # speed_throttle must be a value between -1.0 and 1.0
    ESC.throttle = speed_throttle

def set_steering_angle(angle):
    # angle must be a value between 0 and 180
    Direction_Servo.angle = max(0, min(180, angle)) # Clamp angle to valid range

def stop_robot(): # Renamed from 'stop' for consistency
    set_steering_angle(82)
    set_robot_speed(ROBOT_SPEED_STOP) # Use ROBOT_SPEED_STOP

# ---------- Main Robot Control Loop (ASYNC) ----------
async def main_robot_loop(): # Renamed from Main_Loop for consistency and best practice
    global steering_command # Declare as global as it's modified and used across the loop

    while start_button.value:
        if DEBUG_MODE == 1:
            print("Waiting for start button press...")
        await asyncio.sleep(0.2)
    
    print("Button press detected, starting program now")

    while True:
        #Read all the data asynchromously
        await gyro_reading() 
        current_tof_distances = await read_multiple_tof_sensors()

        # Unpack distances into descriptive variables (assuming 8 sensors as per xshut_pins)
        # This block now correctly handles cases where fewer than 8 sensors initialized
        front_dist = float('inf')
        diagonal_left_front_dist = float('inf')
        diagonal_right_front_dist = float('inf')
        left_middle_dist = float('inf')
        right_middle_dist = float('inf')
        left_rear_dist = float('inf')
        right_rear_dist = float('inf')
        back_dist = float('inf')

        # Assign distances if available, otherwise they remain 'inf'
        if len(current_tof_distances) > 0: front_dist = current_tof_distances[0]
        if len(current_tof_distances) > 1: diagonal_left_front_dist = current_tof_distances[1]
        if len(current_tof_distances) > 2: diagonal_right_front_dist = current_tof_distances[2]
        if len(current_tof_distances) > 3: left_middle_dist = current_tof_distances[3]
        if len(current_tof_distances) > 4: right_middle_dist = current_tof_distances[4]
        if len(current_tof_distances) > 5: left_rear_dist = current_tof_distances[5]
        if len(current_tof_distances) > 6: right_rear_dist = current_tof_distances[6]
        if len(current_tof_distances) > 7: back_dist = current_tof_distances[7]

        steering_command = 0 # Default to straight (0: straight, -1: turn right, 1: turn left)

        if front_dist<=TARGET_DISTANCE_FORWARD and right_middle_dist >= (left_middle_dist + SENSOR_DIFFERENCE_SIDEWAYS) and steering_command<=0: # i need to organize what its gonna make them choose to go right
            steering_command = 1
            if MOVEMENT_MODE == 1:
                set_robot_speed(ROBOT_SPEED_TURN)
                set_steering_angle(81 + Turning_Value)
        #steering command on 1 means its moving to the right
        elif front_dist<=TARGET_DISTANCE_FORWARD and left_middle_dist >= (right_middle_dist + SENSOR_DIFFERENCE_SIDEWAYS) and steering_command>=0: #i need to organize what its gonna make them choose to go left
            steering_command = -1
            if MOVEMENT_MODE == 1:
                set_robot_speed(ROBOT_SPEED_TURN)
                set_steering_angle(81 - Turning_Value)
        #steering command on 1 means its moving to the left
        else:
            steering_command = 0
            if MOVEMENT_MODE == 1:
                set_robot_speed(ROBOT_SPEED_FORWARD_NORMAL)
                set_steering_angle(81)
        #steering command on 0 means its moving forward
        
        if turns >= 12: # If robot has completed 12 turns
            if MOVEMENT_MODE == 1:
                if front_dist >= 100 and back_dist >= 100:
                    stop_robot()
            if DEBUG_MODE == 1:
                print("Done 12 turns, stopping now")
            await asyncio.sleep(2) # Give it time to register stop and message

        # 4. Debugging Output
        if DEBUG_MODE == 1:
            distances_str = ", ".join([f"ToF{i}: {d:.1f}cm" for i, d in enumerate(current_tof_distances)])
            print(f"Distancias ToF: [{distances_str}]")
            # yaw_deg is now the continuously unwrapped angle
            print(f"Angulo Z acumulado: {yaw_deg:.2f}°") 
            print(f"Cruces hechos (turns): {turns}")
            print(f"Angulo de dirección del servo: {Direction_Servo.angle:.2f}°")
            # Additional debug print for current movement state

        await asyncio.sleep(0.05) # Main loop delay

# --- Start the asyncio event loop ---
asyncio.run(main_robot_loop())