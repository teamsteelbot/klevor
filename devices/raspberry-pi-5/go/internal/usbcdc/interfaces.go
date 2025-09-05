package usbcdc

import (
	"context"
)

type (
	// Handler is the interface to manage the USB CDC communication.
	Handler interface {
		Run(ctx context.Context, stopFn func()) error
		GetIncomingMessagesChannel() <-chan *IncomingMessage
		IsRunning() bool
		IsClosed() bool
		NewSender() (Sender, error)
		ReceivedInitializationMessage() bool
	}

	// Sender is the interface to send messages through USB CDC.
	Sender interface {
		SendMessage(message *OutgoingMessage) error
		SendOKMessage() error
		SendStopMessage() error
		SendHeartbeatMessage() error
		IsClosed() bool
		Close()
	}
)
