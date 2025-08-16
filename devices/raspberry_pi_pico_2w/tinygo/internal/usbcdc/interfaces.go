package usbcdc

import (
	"strings"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc/enums"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		ReceiveMessages() (*[]IncomingMessage, error)
		SendMessage(message *OutgoingMessage) error
		SendBufferMessage(
			category enums.OutgoingCategory,
			content *strings.Builder,
		) error
		SendConfirmationMessage() error
		WaitForConfirmationMessage(
			messageToConfirm *OutgoingMessage,
			timeout time.Duration,
		) error
		SendInitializationMessage() error
		SendChallengeMessage() error
		SendBNO08XYawDegreesMessage(yawDegrees float64) error
		SendBNO08XYawTurnsMessage(turns int) error
		SendErrorMessage(err error) error
		Start() error
		Stop()
	}
)
