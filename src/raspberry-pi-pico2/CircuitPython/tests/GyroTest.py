import board
import busio
import math
import time
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (BNO_REPORT_GYROSCOPE, BNO_REPORT_ROTATION_VECTOR)

#GP0 is assigned to SDA, and GP1 is assigned to SCL
i2c = busio.I2C(board.GP1, board.GP0)

try:
    #You may or may not need to force an I2C address, so you can change this to simply:
    #bno = BNO08X_I2C(i2c)
    bno = BNO08X_I2C(i2c, address=0x4B)
    print("Gyroscope started correctly")
except Exception as e:
    print(f"ERROR, Gyro failed to start: {e}")
    while True:
        time.sleep(1)

bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

# This function receives the 4 components of the quaternion and calculates the orientation
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

# ---Main Loop---
while True:
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

        # Print the results
        print(
            "X_g: %6.2f, Y_g: %6.2f, Z_g: %6.2f | R: %6.2f, P: %6.2f, Y: %6.2f" %
            (gyro_x_deg, gyro_y_deg, gyro_z_deg, roll_deg, pitch_deg, yaw_deg)
        )

    except Exception as e:
        print(f"ERROR: {e}")

    time.sleep(0.05)