package usbcdc

import (
	"context"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Handler is the interface to manage the USB CDC communication.
	Handler interface {
		Run(ctx context.Context, stopFn func()) error
		IsRunning() bool
		IsClosed() bool
		NewSender() (Sender, error)
		ReceivedInitializationMessage() bool
		ReceivedStartMessage() bool
		ReceivedChallenge() internal.Challenge
		ReceivedMaxMotorSpeedValue() uint16
		ReceivedMaxServoDirectionValue() uint16
		GetTurns() int
		ReceivedBNO08XYawDegrees() float64
		ReceivedBNO08XPitchDegrees() float64
		ReceivedBNO08XRollDegrees() float64
		ReceivedBNO08XQuaternionX() float64
		ReceivedBNO08XQuaternionY() float64
		ReceivedBNO08XQuaternionZ() float64
		ReceivedBNO08XQuaternionW() float64	
		WaitForChallenge(ctx context.Context) (internal.Challenge, error)
		WaitForMaxMotorSpeedValue(ctx context.Context) (uint16, error)
		WaitForMaxServoDirectionValue(ctx context.Context) (uint16, error)
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
