package usbcdc

type (
	// IncomingMessage is the struct to handle the buffers received to the Raspberry Pi 5
	IncomingMessage struct {
		Category IncomingCategory
		Data     []byte
	}
)

// NewIncomingMessage creates a new instance of IncomingMessage
//
// Parameters:
//
// category: The category of the incoming message
// data: The data buffer of the incoming message
//
// Returns:
//
// An instance of IncomingMessage
func NewIncomingMessage(
	category IncomingCategory,
	data []byte,
) IncomingMessage {
	return IncomingMessage{
		Category: category,
		Data:     data,
	}
}

// IsAServoMessage checks if the IncomingMessage is a servo-related buffer
//
// Returns:
//
// True if the buffer is related to servo operations, otherwise False
func (i *IncomingMessage) IsAServoMessage() bool {
	return i.Category.IsAServoCategory()
}

// IsAMotorMessage checks if the IncomingMessage is a motor-related buffer
//
// Returns:
//
// True if the buffer is related to motor operations, otherwise False
func (i *IncomingMessage) IsAMotorMessage() bool {
	return i.Category.IsAMotorCategory()
}