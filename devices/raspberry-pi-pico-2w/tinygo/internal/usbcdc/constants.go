package usbcdc

import (
	"os"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalchallenge "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/challenge"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

const (
	// BaudRate is the baud rate for USB-CDC communication
	BaudRate = 921_600

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// StartAndEndChar is the message start and end character
	StartAndEndChar uint8 = 0x7E

	// ControlChar is the control character
	ControlChar uint8 = 0x7D

	// Uint8BufferSize is the size of the buffer to hold a uint8 value in bytes
	Uint8BufferSize = 1

	// Uint16BufferSize is the size of the buffer to hold a uint16 value in bytes
	Uint16BufferSize = 2

	// Float64BufferSize is the size of the buffer to hold a float64 value in bytes
	Float64BufferSize = 8

	// MaxIncomingMessageDataLength is the maximum size of incoming message data
	MaxIncomingMessageDataLength = 2

	// MaxOutgoingMessageDataLength is the maximum size of outgoing message data
	MaxOutgoingMessageDataLength = Float64BufferSize
)

var (
	// USBCDCHandler is the USB CDC handler for the Raspberry Pi Pico 2W
	USBCDCHandler Handler

	// failedToInitializeUSBMessage is the message printed when USB initialization fails
	failedToInitializeUSBMessage = []byte("Failed to initialize USB-CDC Handler:")
)

func init() {
	// Initialize the USB CDC handler
	usbCDCHandler, err := NewDefaultHandler(
		internalchallenge.ChallengeHandler,
		internalledonboard.OnBoardHandler,
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeUSBMessage, err, true)
		os.Exit(1)
	}
	USBCDCHandler = usbCDCHandler
}
