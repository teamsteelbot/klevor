from asyncio import run
from board import GP0, GP1
from busio import I2C

from lib.bno08x import BNO08XHandler

# Pins
I2C_BUS = I2C(GP1, GP0)

# Initialize the BNO08X handler
bno08x = BNO08XHandler(
    i2c=I2C_BUS,
)

# Calibrate
run(bno08x.calibrate())

while True:
    # Update quaternion
    run(bno08x.update_quaternion())

    print(f"Yaw: {bno08x.yaw:.2f}°, Pitch: {bno08x.pitch:.2f}°, Roll: {bno08x.roll:.2f}°, Turns: {abs(bno08x.turns)}")
