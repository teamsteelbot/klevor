package bno08x

import (
	"strconv"
	"strings"
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

	// BNO08XSimpleService is the BNO08x simple service.
	BNO08XSimpleService ralvarezdevbno08x.BNO08XSimpleService

	// UART is the UART instance for the BNO08x sensor.
	UART *ralvarezdevbno08x.UART

	// InitializeAttempts is the number of attempts to initialize the BNO08x sensor.
	InitializeAttempts = 5
)

func init() {
	// Some delay to be able to debug the BNO08x initial packets
	time.Sleep(5 * time.Second)

	// ----- UART Instance -----

	// Initialize the BNO08x UART instance with default settings.
	for i := 0; i < InitializeAttempts; i++ {
		uart, err := ralvarezdevbno08x.NewUART(
			machine.UART1,
			machine.GPIO8,
			machine.GPIO9,
			machine.GPIO2,
			machine.GPIO3,
			machine.GPIO4,
			PacketBuffer,
			afterReset,
			ralvarezdevbno08x.NewUARTOptions(internal.Logger, true),
			// ralvarezdevbno08x.NewUARTOptions(nil, false),
		)
		if err == tinygotypes.ErrorCodeNil {
			UART = uart
			break
		}
		println("failed to initialize uart bno08x: " + strings.ToUpper(strconv.FormatUint(uint64(err), 16)))
	}
	if UART == nil {
		panic("failed to initialize uart bno08x")
	}
	
	// Get the BNO08X simple service from the UART
	BNO08XSimpleService = UART.GetBNO08X()
}
