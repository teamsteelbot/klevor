package usbcdc

import (
	"time"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		Update() tinygotypes.ErrorCode
		GetIncomingMessages() []*IncomingMessage
		SendMessage(message *OutgoingMessage) tinygotypes.ErrorCode
		SendConfirmationMessage() tinygotypes.ErrorCode
		WaitForConfirmationMessage(
			messageToConfirm *OutgoingMessage,
			timeout time.Duration,
		) tinygotypes.ErrorCode
		SendInitializationMessage() tinygotypes.ErrorCode
		SendChallengeMessage() tinygotypes.ErrorCode
		SendBNO08XQuaternionsMessages(quaternion *[4]float64) tinygotypes.ErrorCode
		SendErrorMessage(err tinygotypes.ErrorCode) tinygotypes.ErrorCode
		SendStartMessage() tinygotypes.ErrorCode
		Stop()
	}
)
