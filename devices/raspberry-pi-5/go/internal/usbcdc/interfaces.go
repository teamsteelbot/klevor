package usbcdc

type (
	// Handler is the interface to manage the USB CDC communication.
	Handler interface {
		Run() error
		GetIncomingMessagesChannel() <-chan *IncomingMessage
		IsRunning() bool
		IsClosed() bool
	}

	// Sender is the interface to send messages through USB CDC.
	Sender interface {
		SendMessage(message *OutgoingMessage) error
		SendConfirmationMessage() error
		IsClosed() bool
		Close()
	}
)
