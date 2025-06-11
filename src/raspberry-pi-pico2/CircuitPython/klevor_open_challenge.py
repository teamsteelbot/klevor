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
I2C_BUS1 = busio.I2C(board.GP27, board.GP26)  # Used for Gyroscope

# General configuration
MOVEMENT_MODE = True
DEBUG_MODE = False

# Movement delay
MOVEMENT_DELAY = 0.1

# Speed Values
SPEED_NORMAL = -0.35
SPEED_TURN = -0.25
SPEED_STOP = 0

# Steering servo configuration
TURNING_VALUE = 25

# ToF Sensors pins and configuration
FRONT_SENSOR_XSHUT_PIN = board.GP4
DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN = board.GP5
DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN = board.GP22
LEFT_MIDDLE_SENSOR_XSHUT_PIN = board.GP7
RIGHT_MIDDLE_SENSOR_XSHUT_PIN = board.GP28
LEFT_REAR_SENSOR_XSHUT_PIN = board.GP13
RIGHT_REAR_SENSOR_XSHUT_PIN = board.GP16
BACK_SENSOR_XSHUT_PIN = board.GP17
TOF_SENSORS_XSHUT_PINS = [FRONT_SENSOR_XSHUT_PIN, DIAGONAL_LEFT_FRONT_SENSOR_XSHUT_PIN,
                          DIAGONAL_RIGHT_FRONT_SENSOR_XSHUT_PIN, LEFT_MIDDLE_SENSOR_XSHUT_PIN,
                          RIGHT_MIDDLE_SENSOR_XSHUT_PIN, LEFT_REAR_SENSOR_XSHUT_PIN, RIGHT_REAR_SENSOR_XSHUT_PIN,
                          BACK_SENSOR_XSHUT_PIN]
TOF_FRONT_SENSOR = 0
TOF_DIAGONAL_LEFT_SENSOR = 1
TOF_DIAGONAL_RIGHT_SENSOR = 2
TOF_LEFT_MIDDLE_SENSOR = 3
TOF_RIGHT_MIDDLE_SENSOR = 4
TOF_LEFT_REAR_SENSOR = 5
TOF_RIGHT_REAR_SENSOR = 6
TOF_BACK_SENSOR = 7
TOF_SENSORS_NEW_I2C_ADDRESSES = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37]
TOF_SETUP_DELAY = 0.1
TOF_SHORT_SETUP_DELAY = 0.05
TOF_SENSOR_DELAY = 0.075
TOF_MEASUREMENT_TIMING_BUDGET = 100000
TOF_MEASUREMENT_LIMIT_MM = 3000

# Desired Gyroscope update rate
GYRO_READ_INTERVAL = 0.05  # 50 ms for 20 Hz updates

# Start button pins and delay
START_BUTTON_PIN_IN = board.GP14
START_BUTTON_PIN_OUT = board.GP15
START_BUTTON_DELAY = 0.1

# Distance Thresholds
TARGET_DISTANCE_STOP_BACKWARD = 35
TARGET_DISTANCE_START_BACKWARD = 30

# Steering commands
STEERING_LEFT_COMMAND = -1
STEERING_MIDDLE_COMMAND = 0
STEERING_RIGHT_COMMAND = 1

# Servo pins and configuration
STEERING_SERVO = board.GP18
STEERING_SERVO_PWM_CONFIGURATION = pwmio.PWMOut(STEERING_SERVO, duty_cycle=0, frequency=50)
STEERING_SERVO = servo.Servo(STEERING_SERVO_PWM_CONFIGURATION, actuation_range=180, min_pulse=500, max_pulse=2500)
STEERING_SERVO_CENTER = 90

# Motor pins and configuration
ESC_MOTOR_PIN = board.GP19
ESC_PWM_Configuration = pwmio.PWMOut(ESC_MOTOR_PIN, duty_cycle=0, frequency=50)
ESC = servo.ContinuousServo(ESC_PWM_Configuration, min_pulse=1000, max_pulse=2000)
ESC_SETUP_DELAY = 0.25

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

# List of DigitalInOut objects for XSHUT pins and ToF sensors
vl53l0x_xshut = []
vl53l0x_sensors = []

# ToF sensors measures
tof_sensors_measures = [0, 0, 0, 0, 0, 0, 0, 0]


# ---------- SETUP ----------

def setup():
    global bno, initial_yaw

    # This angle actually takes our steering to go forward
    STEERING_SERVO.angle = STEERING_SERVO_CENTER

    if DEBUG_MODE:
        print("Arming ESC...")
    ESC.throttle = SPEED_STOP  # Set throttle to minimum

    try:
        bno = BNO08X_I2C(I2C_BUS1,
                         address=0x4B)  # Normally you don't need to force and I2C address, but in our case we had to
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
        xshut.value = False  # Keep all sensors off initially
        vl53l0x_xshut.append(xshut)

    # Small synchronous pause to ensure all sensors are off
    time.sleep(TOF_SETUP_DELAY)

    if DEBUG_MODE:
        print("Configuring each ToF Sensor...")
    for i, xshut in enumerate(vl53l0x_xshut):
        if DEBUG_MODE:
            print(f"Activating ToF Sensor {i} and re-addressing...")
        xshut.value = True  # Activate the current sensor (pull XSHUT high)
        time.sleep(TOF_SHORT_SETUP_DELAY)  # Short pause for sensor power-up

        try:
            # Initialize the sensor, should be at 0x29
            sensor = adafruit_vl53l0x.VL53L0X(I2C_BUS0)

            # Change the I2C address of the current sensor to a new unique address
            sensor.set_address(TOF_SENSORS_NEW_I2C_ADDRESSES[i])
            vl53l0x_sensors.append(sensor)

            # Set the ToF measurement timing budget
            sensor.measurement_timing_budget = TOF_MEASUREMENT_TIMING_BUDGET

            if DEBUG_MODE:
                print(f"Sensor {i} successfully re-addressed to {hex(TOF_SENSORS_NEW_I2C_ADDRESSES[i])} and ACTIVE.")

            time.sleep(TOF_SHORT_SETUP_DELAY)  # Small synchronous pause before activating next sensor
        except ValueError as e:
            if DEBUG_MODE:
                print(f"ERROR: No VL53L0X device found for Sensor {i} at address 0x29.")
                print(f"Detailed Error: {e}")
            break  # Exit the loop if a sensor fails to initialize

    if len(vl53l0x_sensors) != len(TOF_SENSORS_XSHUT_PINS):
        if DEBUG_MODE:
            print("Error: At least one ToF sensor failed to initialize")
        while True:
            time.sleep(1)

    # Gathering multiple samples to fix errors
    N = 10
    for _ in range(N):
        quat = bno.quaternion
        time.sleep(GYRO_READ_INTERVAL)

    # Saving the orientation, this makesthe turns variables much smoother to handle
    quat = bno.quaternion
    _, _, initial_yaw_val = quaternion_to_euler_degrees(*quat)
    initial_yaw = initial_yaw_val
    if DEBUG_MODE:
        print(f"Initial yaw captured: {initial_yaw:.2f} degrees")
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
    pitch_rad = math.asin(min(1, max(-1, sinp)))  # Clamp value to avoid domain errors for asin

    # Yaw
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw_rad = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll_rad), math.degrees(pitch_rad), math.degrees(yaw_rad)


# Gyroscope Reading Function (now runs as a background task)
async def gyro_reading():
    global initial_yaw, last_raw_yaw, yaw_deg, turns, last_segment_count

    while True:  # Keep reading indefinitely in the background
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

        await asyncio.sleep(GYRO_READ_INTERVAL)


# ---------- Distance Reading Function ----------
async def multiple_tof_sensors_reading():
    while True:
        # Iterate over the 'sensors' list which only contains successfully initialized sensors
        for i, sensor in enumerate(vl53l0x_sensors):
            try:
                distance_mm = sensor.range
                if distance_mm is None or distance_mm < 0:
                    pass
                if distance_mm >= TOF_MEASUREMENT_LIMIT_MM:
                    distance_cm = float('inf')
                else:
                    distance_cm = distance_mm / 10  # Convert to centimeters

                if len(tof_sensors_measures) < len(vl53l0x_sensors):
                    tof_sensors_measures.append(distance_cm)
                else:
                    tof_sensors_measures[i] = distance_cm

                await asyncio.sleep(TOF_SENSOR_DELAY)

            except Exception as e:
                if DEBUG_MODE:
                    print(f"Error reading ToF sensor {i}: {e}")  # Specific error message for ToF


# ---------- Movement Functions ----------

def set_robot_speed(speed_throttle):
    # Must be a value between -1.0 and 1.0
    if speed_throttle < -1.0:
        speed_throttle = -1.0
    elif speed_throttle > 1.0:
        speed_throttle = 1.0
    ESC.throttle = speed_throttle


def set_steering_angle(angle):
    # Must be a value between 0 and 180
    STEERING_SERVO.angle = max(0, min(180, angle))  # Clamp angle to valid range


def stop_robot():  # Renamed from 'stop' for consistency
    set_steering_angle(STEERING_SERVO_CENTER)
    set_robot_speed(SPEED_STOP)  # Use SPEED_STOP


# ---------- Main Robot Control Loop (ASYNC) ----------
async def main_robot_loop():
    global turns

    # Initialize with the current global turns value
    last_known_turns = turns

    # Set the initial steering command as middle
    steering_command = STEERING_MIDDLE_COMMAND
    motor_command = MOTOR_FORWARD
    going_backward = False
    went_backward = False
    waiting_wall = True
    initial_turns = 0

    # Call the setup function
    setup()

    # Start the gyroscope reading as a separate background task
    asyncio.create_task(gyro_reading())

    # Start the ToF sensors reading as a separate background task
    asyncio.create_task(multiple_tof_sensors_reading())

    await asyncio.sleep(TOF_SENSOR_DELAY * len(vl53l0x_sensors))

    # Ensure we can access the global 'turns'
    while True:
        front_dist = tof_sensors_measures[TOF_FRONT_SENSOR]
        diagonal_left_dist = tof_sensors_measures[TOF_DIAGONAL_LEFT_SENSOR]
        diagonal_right_dist = tof_sensors_measures[TOF_DIAGONAL_RIGHT_SENSOR]
        right_middle_dist = tof_sensors_measures[TOF_RIGHT_MIDDLE_SENSOR]
        left_middle_dist = tof_sensors_measures[TOF_LEFT_MIDDLE_SENSOR]
        right_rear_dist = tof_sensors_measures[TOF_RIGHT_REAR_SENSOR]
        left_rear_dist = tof_sensors_measures[TOF_LEFT_REAR_SENSOR]
        back_dist = tof_sensors_measures[TOF_BACK_SENSOR]

        # --- Check for Gyro Turn and Center Servo Immediately ---
        # This logic takes precedence for centering the servo upon a new 'turn' detection
        if turns != last_known_turns:
            if DEBUG_MODE:
                print(f"**Turn detected: {turns} (before {last_known_turns}) - Centering Servo**")
            set_steering_angle(STEERING_SERVO_CENTER)
            steering_command = STEERING_MIDDLE_COMMAND  # Override command to center for this cycle
            last_known_turns = turns  # Update for the next check
            # No need to set motor speed here, as the regular navigation logic will handle it below.
            # We just ensure the servo is centered and the steering command is reset.

        # --- Overall Mission Completion Check ---
        if abs(turns) == 12:  # If robot has completed 12 turns
            if MOVEMENT_MODE:
                motor_command = MOTOR_FORWARD
                steering_command = STEERING_MIDDLE_COMMAND
                time.sleep(1)
                await asyncio.sleep(MOVEMENT_DELAY)
            if DEBUG_MODE:
                print("Done 12 turns, stopping now")
            return

        # --- Navigation Logic ---
        # This logic determines the steering_command for the *next* cycle,
        # unless overridden by the turn detection above.
        if waiting_wall:
            if front_dist >= TARGET_DISTANCE_START_BACKWARD or diagonal_left_dist >= TARGET_DISTANCE_START_BACKWARD or diagonal_right_dist >= TARGET_DISTANCE_START_BACKWARD:
                # Only set if not already forced to middle by turn detection
                if steering_command != STEERING_MIDDLE_COMMAND:  # Avoid overwriting if a turn was just detected
                    steering_command = STEERING_MIDDLE_COMMAND
                motor_command = MOTOR_FORWARD

            elif front_dist < TARGET_DISTANCE_START_BACKWARD or diagonal_left_dist < TARGET_DISTANCE_START_BACKWARD or diagonal_right_dist < TARGET_DISTANCE_START_BACKWARD:
                motor_command = MOTOR_BACKWARD
                going_backward = True
                waiting_wall = False

        elif going_backward and (
                front_dist >= TARGET_DISTANCE_STOP_BACKWARD or diagonal_left_dist >= TARGET_DISTANCE_STOP_BACKWARD or diagonal_right_dist >= TARGET_DISTANCE_STOP_BACKWARD):
            motor_command = MOTOR_FORWARD
            going_backward = False
            went_backward = True
            initial_turns = turns  # Store turns for recovery logic

            if right_middle_dist == float('inf') or right_rear_dist == float('inf'):
                steering_command = STEERING_RIGHT_COMMAND

            elif left_middle_dist == float('inf') or left_rear_dist == float('inf'):
                steering_command = STEERING_LEFT_COMMAND

        elif went_backward and initial_turns != turns:  # If robot has turned after backing up
            went_backward = False
            steering_command = STEERING_MIDDLE_COMMAND
            waiting_wall = True

        # Set the speed and angle based on the determined steering_command
        # Note: If a turn was just detected and the servo was centered, this might
        # immediately set it back to a turning angle if the navigation logic dictates so.
        # This is expected behavior with immediate centering.
        if MOVEMENT_MODE:
            if steering_command == STEERING_MIDDLE_COMMAND:
                set_robot_speed(SPEED_NORMAL * motor_command)
                set_steering_angle(STEERING_SERVO_CENTER)  # Ensure it's centered if command is middle
            else:
                set_robot_speed(SPEED_TURN * motor_command)
                set_steering_angle(STEERING_SERVO_CENTER - steering_command * TURNING_VALUE)

        if DEBUG_MODE:
            print(f"""Turns: {turns}
ToF Distances: [{", ".join([f"ToF{i}: {d:.1f}cm" for i, d in enumerate(tof_sensors_measures)])}]
Accumulated Angle Z: {yaw_deg:.2f}°
Motor Direction: {"Going forward" if motor_command == MOTOR_FORWARD else "Going backward"}
Motor Speed: {str(SPEED_NORMAL * motor_command)}
Servo Angle: {STEERING_SERVO.angle:.2f}°
Waiting Wall: {"Yes" if waiting_wall else "No"}
Going Backward: {"Yes" if going_backward else "No"}
Went Backward: {"Yes" if went_backward else "No"}
{"-" * 40}
""")
        await asyncio.sleep(MOVEMENT_DELAY)


# Start the asyncio event loop
asyncio.run(main_robot_loop())

