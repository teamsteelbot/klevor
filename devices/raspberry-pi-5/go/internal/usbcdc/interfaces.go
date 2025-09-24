package usbcdc

import (
	"context"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Handler is the interface to manage the USB CDC communication.
	Handler interface {
		Run(ctx context.Context, cancelFn context.CancelFunc) error
		IsRunning() bool
		NewSender() (Sender, error)
		ReceivedStartMessage() bool
		ReceivedChallenge() internal.Challenge
		Get360DegreeTurns() int
		Get90DegreeTurns() int
		Get45DegreeTurns() int
		Get30DegreeTurns() int
		GetAccumulatedYawDegrees() float64
		ReceivedBNO08XYawDegrees() float64
		ReceivedBNO08XPitchDegrees() float64
		ReceivedBNO08XRollDegrees() float64
		ReceivedBNO08XQuaternionX() float64
		ReceivedBNO08XQuaternionY() float64
		ReceivedBNO08XQuaternionZ() float64
		ReceivedBNO08XQuaternionW() float64
		WaitForChallenge(ctx context.Context) (internal.Challenge, error)
		WaitMotorSpeedStartMessage(ctx context.Context) error
		WaitMotorSpeedEndMessage(ctx context.Context) error
		ClearMotorSpeedStartAndEndMessagesCh()
		WaitServoAngleStartMessage(ctx context.Context) error
		WaitServoAngleEndMessage(ctx context.Context) error
		ClearServoAngleStartAndEndMessagesCh()
		WaitUntilReady(ctx context.Context) error
	}

	// Sender is the interface to send messages through USB CDC.
	Sender interface {
		SendMessage(message *OutgoingMessage) error
		SendOKMessage() error
		IsClosed() bool
		Close()
	}
)
