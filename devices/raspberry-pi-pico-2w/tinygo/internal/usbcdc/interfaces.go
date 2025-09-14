package usbcdc

import (
	"time"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		Update() tinygotypes.ErrorCode
		SendMessage(message OutgoingMessage) tinygotypes.ErrorCode		
		SendBNO08XQuaternionsMessages(quaternion [4]float64) tinygotypes.ErrorCode
		SendBNO08XEulerDegreesMessages(eulerDegrees [3]float64) tinygotypes.ErrorCode
		SendInitializationMessage() tinygotypes.ErrorCode
		SendChallengeMessage() tinygotypes.ErrorCode
		SendErrorMessage(err tinygotypes.ErrorCode) tinygotypes.ErrorCode
		SendStartMessage() tinygotypes.ErrorCode
		SendConfirmationMessage() tinygotypes.ErrorCode
		WaitForConfirmationMessage(
			timeout time.Duration,
		) tinygotypes.ErrorCode
		Stop()
	}
)
