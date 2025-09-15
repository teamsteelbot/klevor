package usbcdc

import (
	"time"

	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		IsAvailableToRead() bool
		ReadMessage(timeout time.Duration) (IncomingMessage, tinygoerrors.ErrorCode)
		SendMessage(message OutgoingMessage) tinygoerrors.ErrorCode
		SendBNO08XQuaternionMessages(quaternion [4]float64) tinygoerrors.ErrorCode
		SendBNO08XEulerDegreesMessages(eulerDegrees [3]float64) tinygoerrors.ErrorCode
		SendInitializationMessage() tinygoerrors.ErrorCode
		SendChallengeMessage() tinygoerrors.ErrorCode
		SendErrorMessage(err tinygoerrors.ErrorCode) tinygoerrors.ErrorCode
		SendStartMessage() tinygoerrors.ErrorCode
		SendConfirmationMessage() tinygoerrors.ErrorCode
		SendMaxMotorSpeedValueMessage(maxMotorSpeed uint16) tinygoerrors.ErrorCode
		SendMaxServoDirectionValueMessage(maxServoDirection uint16) tinygoerrors.ErrorCode
		WaitForConfirmationMessage(
			timeout time.Duration,
		) tinygoerrors.ErrorCode
		Stop()
	}
)
