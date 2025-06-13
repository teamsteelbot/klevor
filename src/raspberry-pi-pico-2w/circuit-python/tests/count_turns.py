#-----------------------------LIBRARIES----------------------------
import board
import pwmio
import busio
import math
import time
import digitalio
from adafruit_motor import servo
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)

# ---------- Initialize both I2C buses ----------

i2c_bus0 = busio.I2C(board.GP1, board.GP0)
i2c_bus1 = busio.I2C(board.GP3, board.GP2)

#----------------VARIABLES----------------

DEBUG_MODE = 1
global yaw_deg, turns
turns = 0
#It's very important that these values are correct or else the code could break itself pretty much

#------------------------SETUP--------------------------------

#Check that the gyro starts up correctly
try: 
    bno = BNO08X_I2C(i2c_bus0, address=0x4B)
except Exception as e:
    if DEBUG_MODE == 1:
        print(f"ERROR, Gyro failed to start: {e}")
    while True:
        time.sleep(1)


#Enabling features onto the gyro now that the RPI Pico knows which direction it is (i could skip some lines of code but it makes debugging harder)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

def quaternion_to_euler_degrees(x, y, z, w):
    # Roll
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll_rad = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch
    sinp = 2 * (w * y - z * x)
    # Clamp the value to avoid domain errors for asin (should be between -1 and 1)
    if sinp > 1:
        pitch_rad = math.pi / 2
    elif sinp < -1:
        pitch_rad = -math.pi / 2
    else:
        pitch_rad = math.asin(sinp)

    # Yaw
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw_rad = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll_rad), math.degrees(pitch_rad), math.degrees(yaw_rad)

def gyro_reading():   
    try:
        # ---Reading the Gyroscope Data---
        x_rad, y_rad, z_rad = bno.gyro
        gyro_x_deg = math.degrees(x_rad)
        gyro_y_deg = math.degrees(y_rad)
        gyro_z_deg = math.degrees(z_rad)

        # ---Reading the quaternion data---
        quat_x, quat_y, quat_z, quat_w = bno.quaternion

        #Calling the quaternion_to_euler_degrees function to calculate the current orientation
        roll_deg, pitch_deg, yaw_deg = quaternion_to_euler_degrees(quat_x, quat_y, quat_z, quat_w)

    except Exception as e:
        if DEBUG_MODE == 1:
            print(f"ERROR: {e}")
    return yaw_deg

while True:
    gyro_reading()
    if yaw_deg>= 90 or yaw_deg<= -90:
        yaw_sign = 1 if yaw_deg>=0 else -1
        yaw_deg = (abs(yaw_deg) - 90) * yaw_sign
        turns +=1
    if DEBUG_MODE == 1:
        print(f"Angulo Z acumulado: {yaw_deg}")
        print(f"Cruces hechos: {turns}")
        time.sleep(1)
    time.sleep(0.05)