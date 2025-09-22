package usbcdc

import (
	"time"

	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

type (
	// Handler is the interface to manage the USB CDC connection.
	Handler interface {
		IsAvailableToRead() bool
		ReadMessage(timeout time.Duration) (
			IncomingMessage,
			tinygoerrors.ErrorCode,
		)
		SendMessage(message OutgoingMessage) tinygoerrors.ErrorCode
		SendBNO08XQuaternionMessages(quaternion [4]float64) tinygoerrors.ErrorCode
		SendBNO08XEulerDegreesMessages(eulerDegrees [3]float64) tinygoerrors.ErrorCode
		SendChallengeMessage() tinygoerrors.ErrorCode
		SendErrorMessage(err tinygoerrors.ErrorCode) tinygoerrors.ErrorCode
		SendStartMessage() tinygoerrors.ErrorCode
		SendConfirmationMessage() tinygoerrors.ErrorCode
		// SendMaxMotorSpeedValueMessage(maxMotorSpeed uint16) tinygoerrors.ErrorCode
		// SendMaxServoAngleValueMessage(maxServoAngle uint16) tinygoerrors.ErrorCode
		SendHeartbeatMessage() tinygoerrors.ErrorCode
		SendMotorSpeedStartMessage() tinygoerrors.ErrorCode
		SendMotorSpeedEndMessage() tinygoerrors.ErrorCode
		SendServoAngleStartMessage() tinygoerrors.ErrorCode
		SendServoAngleEndMessage() tinygoerrors.ErrorCode
		WaitForConfirmationMessage(
			timeout time.Duration,
		) tinygoerrors.ErrorCode
		Stop()
	}
)
