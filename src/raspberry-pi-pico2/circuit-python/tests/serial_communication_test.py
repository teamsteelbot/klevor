import usb_cdc
from time import sleep

while True:
    # Check whether any data has been sent
    if usb_cdc.data.in_waiting > 0:
        # read next line of waiting data ending in line ending ('\n')
        data_received = usb_cdc.data.readline().strip().decode("utf-8")
        # Print data to console
        print(f"Message received: {data_received}")
        
    
    sleep(0.05)