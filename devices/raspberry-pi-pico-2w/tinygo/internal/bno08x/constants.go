package bno08x

import (
	"os"
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	tinygobno08x "github.com/ralvarezdev/tinygo-bno08x"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
)

var (
	// PacketBuffer is the default packet buffer for the BNO08x sensor.
	PacketBuffer = tinygobno08x.NewDefaultPacketBuffer()

	// YawDegreesDifference is the difference in degrees to consider a yaw change.
	YawDegreesDifference = 1.0

	// UART is the UART instance for the BNO08x sensor.
	UART *tinygobno08x.UART

	// UARTRVC is the UART-RVC instance for the BNO08x sensor.
	UARTRVC *tinygobno08x.UARTRVC

	// Interval is the interval to read the sensor data.
	Interval = 10 * time.Millisecond // Can be as low as 10ms

	// failedToInitializeBNO08xErrorMessage is the error message for failed BNO08x initialization.
	failedToInitializeBNO08xErrorMessage = []byte("Failed to initialize BNO08x sensor")
)

func init() {
	// Some delay to be able to debug the BNO08x initial packets
	// time.Sleep(5 * time.Second)

	/*
		// ----- UART Instance -----

		// Initialize the BNO08x UART instance with default settings.
		uart, err := tinygobno08x.NewUART(
			machine.UART1,
			machine.GPIO8,
			machine.GPIO9,
			machine.GPIO2,
			machine.GPIO3,
			machine.GPIO4,
			PacketBuffer,
			afterReset,
			internal.Logger,
			true,
		)
		if err != tinygoerrors.ErrorCodeNil {
			internal.Logger.WarningMessageWithErrorCode(failedToInitializeBNO08xErrorMessage, err, true)
			os.Exit(1)
		}
		UART = uart
	*/

	// ----- UART-RVC Instance -----

	// Initialize the BNO08x UART-RVC instance with default settings.
	uartRVC, err := tinygobno08x.NewUARTRVC(
		machine.UART1,
		machine.GPIO8,
		machine.GPIO9,
		machine.GPIO2,
		machine.GPIO3,
		machine.GPIO4,
		nil, // internal.Logger
	)
	if err != tinygoerrors.ErrorCodeNil {
		internal.Logger.WarningMessageWithErrorCode(
			failedToInitializeBNO08xErrorMessage,
			err,
			true,
		)
		os.Exit(1)
	}
	UARTRVC = uartRVC
}
