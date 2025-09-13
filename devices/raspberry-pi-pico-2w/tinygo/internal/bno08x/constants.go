package bno08x

import (
	"time"

	"machine"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"

	//ralvarezdevbno08x "github.com/ralvarezdev/go-bno08x"
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

var (
	// PacketBuffer is the default packet buffer for the BNO08x sensor.
	PacketBuffer = ralvarezdevbno08x.NewDefaultPacketBuffer()

	// YawDegreesDifference is the difference in degrees to consider a yaw change.
	YawDegreesDifference = 1.0

	// UART is the UART instance for the BNO08x sensor.
	UART *ralvarezdevbno08x.UART

	// UARTRVC is the UART-RVC instance for the BNO08x sensor.
	UARTRVC *ralvarezdevbno08x.UARTRVC

	// failedToInitializeBNO08xErrorMessage is the error message for failed BNO08x initialization.
	failedToInitializeBNO08xErrorMessage = []byte("Failed to initialize BNO08x sensor")
)

func init() {
	// Some delay to be able to debug the BNO08x initial packets
	time.Sleep(5 * time.Second)

	/*
	// ----- UART Instance -----

	// Initialize the BNO08x UART instance with default settings.
	uart, err := ralvarezdevbno08x.NewUART(
		machine.UART1,
		machine.GPIO8,
		machine.GPIO9,
		machine.GPIO2,
		machine.GPIO3,
		machine.GPIO4,
		PacketBuffer,
		afterReset,
		ralvarezdevbno08x.NewUARTOptions(internal.Logger, false),
		// ralvarezdevbno08x.NewUARTOptions(nil, false),
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.WarningMessageWithErrorCode(failedToInitializeBNO08xErrorMessage, err, true)
		return
	}
	UART = uart
	*/

	// ----- UART-RVC Instance -----

	// Initialize the BNO08x UART-RVC instance with default settings.
	uartRVC, err := ralvarezdevbno08x.NewUARTRVC(
		machine.UART1,
		machine.GPIO8,
		machine.GPIO9,
		machine.GPIO2,
		machine.GPIO3,
		machine.GPIO4,
		ralvarezdevbno08x.NewUARTRVCOptions(
			internal.Logger,
		),
	)
	if err != tinygotypes.ErrorCodeNil {
		internal.Logger.WarningMessageWithErrorCode(failedToInitializeBNO08xErrorMessage, err, true)
		return
	}
	UARTRVC = uartRVC
}
