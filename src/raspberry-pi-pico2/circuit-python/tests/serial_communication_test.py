import usb_cdc
from time import sleep

# Times to read data before sending stop message
READ_TIMES_LIMIT = 100

# Send start message to the device
usb_cdc.data.write(b"status:on\n")

read_times = 0
while read_times < READ_TIMES_LIMIT:
    # Check whether any data has been sent
    if usb_cdc.data.in_waiting > 0:
        # Read next line of waiting data ending in line ending ('\n')
        data_received = usb_cdc.data.readline().strip().decode("utf-8")
    
    read_times += 1
    sleep(0.05)

# Send stop message to the device
usb_cdc.data.write(b"status:off\n")
