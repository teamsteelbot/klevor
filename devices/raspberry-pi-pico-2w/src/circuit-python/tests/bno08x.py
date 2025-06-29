from asyncio import run, create_task
from board import GP0, GP1
from busio import I2C

from lib.bno08x import BNO08XHandler
from lib.enums import QuaternionAxis

# Constants
QUATERNION_HORIZONTAL_AXIS = QuaternionAxis.YAW

# Pins
I2C_BUS = I2C(GP1, GP0)

# Initialize the BNO08X handler
bno08x = BNO08XHandler(
    horizontal_axis=QUATERNION_HORIZONTAL_AXIS,
    i2c=I2C_BUS,
)

# Calibrate
run(bno08x.calibrate())

while True:
    # Update quaternion
    run(bno08x.update_quaternion())

    print(f"Yaw: {bno08x.quaternion.yaw:.2f}°, "
          f"Pitch: {bno08x.quaternion.pitch:.2f}°, "
          f"Roll: {bno08x.quaternion.roll:.2f}°")
