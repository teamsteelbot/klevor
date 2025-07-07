from .enums import IncomingCategory, OutgoingCategory, Status
from .message import IncomingMessage, OutgoingMessage

# Stop message
STOP_MESSAGE = OutgoingMessage(
    OutgoingCategory.STATUS, Status.STOP.parsed_name
)

# Confirmation message
OUTGOING_OK_MESSAGE = OutgoingMessage(
    OutgoingCategory.STATUS, Status.OK.parsed_name
)
INCOMING_OK_MESSAGE = IncomingMessage(
    IncomingCategory.STATUS, Status.OK.parsed_name
)

# Heartbeat message
HEARTBEAT_MESSAGE = OutgoingMessage(
    OutgoingCategory.STATUS, Status.HEARTBEAT.parsed_name
)
