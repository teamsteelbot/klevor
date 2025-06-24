from .enums import OutgoingCategory, Status
from .message import IncomingMessage, OutgoingMessage

# Raspberry Pi Pico baud rate
RASPBERRY_PI_PICO_BAUDRATE = 115200

# Raspberry PI Pico console port
RASPBERRY_PI_PICO_CONSOLE_PORT = '/dev/ttyACM0'
RASPBERRY_PI_PICO_CONSOLE_PORT_ALT = '/dev/ttyACM2'

# Raspberry PI Pico data port
RASPBERRY_PI_PICO_DATA_PORT = '/dev/ttyACM1'
RASPBERRY_PI_PICO_DATA_PORT_ALT = '/dev/ttyACM3'

# Encode
ENCODE = 'utf-8'

# Common messages
START_MESSAGE = IncomingMessage(OutgoingCategory.STATUS, Status.START)
STOP_MESSAGE = OutgoingMessage(OutgoingCategory.STATUS, Status.STOP)
INCOMING_OK_MESSAGE = IncomingMessage(OutgoingCategory.STATUS, Status.OK)
OUTGOING_OK_MESSAGE = OutgoingMessage(OutgoingCategory.STATUS, Status.OK)
