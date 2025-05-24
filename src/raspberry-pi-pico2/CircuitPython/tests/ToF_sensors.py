import board
import busio
import time
import adafruit_vl53l0x

# --- Initialize I2C bus ---
i2c= busio.I2C(board.GP1, board.GP0)

# The default I2C address for VL53L0X is 0x29
try:
    vl53= adafruit_vl53l0x.VL53L0X(i2c, address = 0x29)
    print("VL53L0X sensor initialized successfully.")
except Exception as e:
    print(f"ERROR: {e}")
    while True:
        time.sleep(1)

#A higher value means more accurate but slower readings.
vl53.measurement_timing_budget = 33000

while True:
    try:
        # The sensor returns distance in millimeters (mm).
        distance_mm = vl53.range

        # Convert to centimeters
        distance_cm = distance_mm / 10.0

        if distance_cm < 300: # Sensor returns ~819cm if no object is detected or out of range (however the maximum range for this sensor is around 2 meters)
            print(f"Distance: {distance_cm:.2f}cm")
        else:
            print("Distance: Out of range / No object detected")


    except Exception as e:
        print(f"ERROR reading sensor data: {e}")
        # This can happen if the sensor disconnects or there's I2C noise.

    time.sleep(0.1)