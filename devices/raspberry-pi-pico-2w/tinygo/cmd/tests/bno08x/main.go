package main

import (
	"os"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
	internalbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x"
	tinygoerrors "github.com/ralvarezdev/tinygo-errors"
	tinygologger "github.com/ralvarezdev/tinygo-logger"
)

var (
	// noBNO08XStructInitializedMessage is the message printed when no BNO08X struct is initialized
	noBNO08XStructInitializedMessage = []byte("No BNO08X struct initialized")

	// failedToUpdateBNO08XMessage is the message printed when updating the BNO08X sensor fails
	failedToUpdateBNO08XMessage = []byte("Failed to update BNO08X sensor")
)

func main() {
	// Check if both BNO08x interfaces are not initialized
	if internalbno08x.UART == nil && internalbno08x.UARTRVC == nil {
		internal.Logger.ErrorMessage(noBNO08XStructInitializedMessage)
		os.Exit(1)
	}

	for {
		/*
			if internalbno08x.UART != nil {
				// Update quaternion
				internalbno08x.UART.Update()

				// Get the quaternion
				q := internalbno08x.UART.GetQuaternion()
				// Log the quaternion values
				internal.PrintQuaternion(q)
			}
		*/

		if internalbno08x.UARTRVC != nil {
			// Update euler degrees
			if err := internalbno08x.UARTRVC.Update(); err != tinygoerrors.ErrorCodeNil {
				internal.Logger.WarningMessageWithErrorCode(
					failedToUpdateBNO08XMessage,
					err,
					true,
				)
			}

			// Get the euler degrees
			e := internalbno08x.UARTRVC.GetEulerDegrees()

			// Log the euler degrees values
			internal.PrintEulerDegrees(e)
		}

		// Print memory stats
		tinygologger.DebugMemory(internal.Logger)
	}
}
