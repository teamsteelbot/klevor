# Raspberry Pi Pico baud rate
RASPBERRY_PI_PICO_BAUDRATE = 115200

# Number of possible Raspberry Pi Pico ports for either console or data communication
POSSIBLE_RASPBERRY_PI_PICO_PORTS = 5

# Raspberry PI Pico console ports
RASPBERRY_PI_PICO_CONSOLE_PORTS = [f"/dev/ttyACM{i * 2}" for i in
                                   range(POSSIBLE_RASPBERRY_PI_PICO_PORTS)]

# Raspberry PI Pico data ports
RASPBERRY_PI_PICO_DATA_PORTS = [f"/dev/ttyACM{i * 2 + 1}" for i in
                                range(POSSIBLE_RASPBERRY_PI_PICO_PORTS)]

# Attempts to connect to the serial port
CONNECTION_ATTEMPTS = 10

# Attempts delay
ATTEMPTS_DELAY = 1

# Stop timeout
STOP_TIMEOUT = 1.0

# Encode
ENCODE = 'utf-8'

# Message header separator
HEADER_SEPARATOR_CHAR = ':'

# Message end character
END_CHAR = '\x04'
