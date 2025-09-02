package usbcdc

type (
	// Handler is the interface to manage the USB CDC communication.
	Handler interface {
		SendOutgoingMessages() error
		ReceiveIncomingMessages() error
	}
)
