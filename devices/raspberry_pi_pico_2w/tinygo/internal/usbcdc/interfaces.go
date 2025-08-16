package usbcdc

import (
	"strings"
	"time"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		ReceiveMessages() (*[]IncomingMessage, error)
		SendMessage(message *OutgoingMessage) error
		SendBufferMessage(category string, content *strings.Builder) error
		SendConfirmationMessage() error
		WaitForConfirmationMessage(
			messageToConfirm *OutgoingMessage,
			timeout time.Duration,
		) error
		SendInitializationMessage() error
		SendChallengeMessage() error
		SendBNO08xYawDegreesMessage(yawDegrees float64) error
		SendBNO08xYawTurnsMessage(turns int) error
		SendErrorMessage(err error) error
		Start() error
		Stop()
	}
)
