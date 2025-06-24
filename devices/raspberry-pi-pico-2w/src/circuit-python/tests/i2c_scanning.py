from board import GP0, GP1
from busio import I2C

# For the Raspberry Pi Pico, the hardware I2C0 bus uses the pins:
# SCL (Clock) = GP1 (Physical pin 2 on the Pico)
# SDA (Data) = GP0 (Physical pin 1 on the Pico)
# If you're using the I2C1 Bus, it would be: I2C(GP3, GP2)
i2c = I2C(GP1, GP0)

# Try to lock the I2C bus. This ensures no other process uses it while scanning.
print("Starting I2C scan...")
while not i2c.try_lock():
    pass  # Active wait until the bus is available

try:
    # Perform the I2C bus scan
    found_devices = i2c.scan()

    if not found_devices:
        print("No I2C devices found on the bus. Check your connections.")

    else:
        print("I2C devices found at the following addresses (hexadecimal):")
        for address in found_devices:
            print(
                f"  - 0x{address:x}"
            )  # Print the address in hexadecimal format

finally:
    i2c.unlock()
