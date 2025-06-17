from machine import Pin, I2C
import time
from vl53l0x import VL53L0X

# Define I2C buses
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
i2c1 = I2C(1, scl=Pin(3), sda=Pin(2), freq=100000)  # Using default pins for I2C1

# Define XSHUT pins for the six sensors
xshut_pins = [
    Pin(4, Pin.OUT, value=0),  # Sensor 1 (I2C0)
    Pin(5, Pin.OUT, value=0),  # Sensor 2 (I2C0)
    Pin(6, Pin.OUT, value=0),  # Sensor 3 (I2C0)
    Pin(7, Pin.OUT, value=0),  # Sensor 4 (I2C1)
    Pin(8, Pin.OUT, value=0),  # Sensor 5 (I2C1)
    Pin(9, Pin.OUT, value=0),  # Sensor 6 (I2C1)
]

# Function to initialize a VL53L0X sensor with a given I2C bus, XSHUT pin, and new address
def initialize_sensor(i2c_bus, xshut_pin, new_address):
    xshut_pin.value(0)
    time.sleep_ms(10)
    xshut_pin.value(1)
    time.sleep_ms(10)
    sensor = VL53L0X(i2c_bus)
    sensor.set_address(new_address)
    return sensor

# Initialize sensors on I2C0
sensor1 = initialize_sensor(i2c0, xshut_pins[0], 0x2A)
sensor2 = initialize_sensor(i2c0, xshut_pins[1], 0x2B)
sensor3 = initialize_sensor(i2c0, xshut_pins[2], 0x2C)

# Initialize sensors on I2C1
sensor4 = initialize_sensor(i2c1, xshut_pins[3], 0x2A)
sensor5 = initialize_sensor(i2c1, xshut_pins[4], 0x2B)
sensor6 = initialize_sensor(i2c1, xshut_pins[5], 0x2C)

print("Sensor 1 ID (I2C0):", hex(sensor1.sensor_id))
print("Sensor 2 ID (I2C0):", hex(sensor2.sensor_id))
print("Sensor 3 ID (I2C0):", hex(sensor3.sensor_id))
print("Sensor 4 ID (I2C1):", hex(sensor4.sensor_id))
print("Sensor 5 ID (I2C1):", hex(sensor5.sensor_id))
print("Sensor 6 ID (I2C1):", hex(sensor6.sensor_id))

try:
    while True:
        # Start ranging for sensors on I2C0
        sensor1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        sensor2.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        sensor3.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

        # Start ranging for sensors on I2C1
        sensor4.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        sensor5.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        sensor6.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

        time.sleep_ms(50)

        # Get readings from sensors on I2C0
        dist1 = sensor1.get_distance()
        dist2 = sensor2.get_distance()
        dist3 = sensor3.get_distance()

        # Get readings from sensors on I2C1
        dist4 = sensor4.get_distance()
        dist5 = sensor5.get_distance()
        dist6 = sensor6.get_distance()

        # Stop ranging for sensors on I2C0
        sensor1.stop_ranging()
        sensor2.stop_ranging()
        sensor3.stop_ranging()

        # Stop ranging for sensors on I2C1
        sensor4.stop_ranging()
        sensor5.stop_ranging()
        sensor6.stop_ranging()

        print("I2C0 - Sensor 1:", dist1, "mm, Sensor 2:", dist2, "mm, Sensor 3:", dist3, "mm")
        print("I2C1 - Sensor 4:", dist4, "mm, Sensor 5:", dist5, "mm, Sensor 6:", dist6, "mm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    sensor1.stop_ranging()
    sensor2.stop_ranging()
    sensor3.stop_ranging()
    sensor4.stop_ranging()
    sensor5.stop_ranging()
    sensor6.stop_ranging()
    