from .enums import OutgoingCategory, Status
from .message import OutgoingMessage, IncomingMessage

# Stop message
STOP_MESSAGE = OutgoingMessage(
    OutgoingCategory.STATUS, Status.STOP.parsed_name
)

# Confirmation message
OUTGOING_OK_MESSAGE = OutgoingMessage(
    OutgoingCategory.STATUS, Status.OK.parsed_name
)
INCOMING_OK_MESSAGE = IncomingMessage(
    OutgoingCategory.STATUS, Status.OK.parsed_name
)