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
		ReceivedBNO08XTurns() int
		ReceivedBNO08XYawDegrees() float64
	}

	// Sender is the interface to send messages through USB CDC.
	Sender interface {
		SendMessage(message *OutgoingMessage) error
		SendOKMessage() error
		IsClosed() bool
		Close()
	}
)
