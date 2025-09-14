package servo

// SetDirectionBasedOnReceivedMessage sets the servo direction based on the received message
//
// Parameters:
//
// message: The incoming message containing the servo direction command
//
// Returns:
//
// An error if the servo direction could not be set
func SetDirectionBasedOnReceivedMessage(message *internalusbcdc.IncomingMessage) tinygotypes.ErrorCode {
	// Check if the message is nil
	if message == nil {
		return internalusbcdc.ErrorCodeUSBCDCNilIncomingMessage
	}

	// Check if the servo angle should be retrieved from the message
	var servoDirectionAngle uint16
	if message.Category != internalusbcdc.IncomingCategoryServoDirectionCenter {
		// Get uint16 angle from message content
		angle, err := message.GetContentAsUint16()
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeServoInvalidAngleValue
		}
		servoDirectionAngle = angle
	}

	// Check the servo angle category
	switch message.Category {
	case internalusbcdc.IncomingCategoryServoDirectionCenter:
		return s.SetDirectionToCenter()
	case internalusbcdc.IncomingCategoryServoDirectionToLeft:
		return s.SetDirectionToLeft(servoDirectionAngle)
	case internalusbcdc.IncomingCategoryServoDirectionToRight:
		return s.SetDirectionToRight(servoDirectionAngle)
	default:
		return ErrorCodeServoUnknownAngleCategory
	}
}
