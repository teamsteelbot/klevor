package bno08x

import (
	"time"

	"machine"

	ralvarezdevbno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	//ralvarezdevbno08x "github.com/ralvarezdev/go-bno08x"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

var (
	// DataBuffer is the default data buffer size for the BNO08x sensor.
	DataBuffer = ralvarezdevbno08x.NewDefaultDataBuffer()

	// YawDegreesDifference is the difference in degrees to consider a yaw change.
	YawDegreesDifference = 1.0

	// ResetBNO08XInterval is the interval to reset the BNO08x sensor to prevent overflow.
	ResetBNO08XInterval = 2 * time.Minute

	// BNO08XService is the BNO08x service.
	BNO08XService ralvarezdevbno08x.BNO08XService

	// I2C is the I2C instance for the BNO08x sensor.
	// I2C *bno08x.I2C

	// UART is the UART instance for the BNO08x sensor.
	UART *ralvarezdevbno08x.UART

	// UARTRVC is the UART-RVC instance for the BNO08x sensor.
	// UARTRVC *ralvarezdevbno08x.UARTRVC

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
			DataBuffer,
			afterSoftwareReset,
			ralvarezdevbno08x.NewUARTOptions(ralvarezdevbno08x.NewDefaultDebugger(), true),
			// ralvarezdevbno08x.NewUARTOptions(nil, false),
		)
		if err == nil {
			UART = uart
			break
		}
		
	}

	if UART == nil {
		panic("failed to initialize uart bno08x")
	}

	// Get the BNO08X service from the UART
	BNO08XService = UART.GetBNO08XService()

	/*
		// ----- I2C Instance -----

		// Initialize the BNO08x I2C instance with default settings.
		address0 := machine.GPIO0
		i2c, err := ralvarezdevbno08x.NewI2C(
			machine.I2C1,
			machine.GPIO26,
			machine.GPIO27,
			ralvarezdevbno08x.I2CAlternativeAddress,
			machine.GPIO2,
			machine.GPIO3,
			machine.GPIO4,
			DataBuffer,
			nil, 
			afterSoftwareReset,
			ralvarezdevbno08x.NewI2COptions(ralvarezdevbno08x.NewDefaultDebugger(), &address0),
		)
		if err != nil {
			panic("failed to initialize i2c bno08x: " + err.Error())
		}
		I2C = i2c

		// Enable quaternion feature
		if err = I2C.EnableFeature(ralvarezdevbno08x.ReportIDRotationVector); err != nil {
			panic("failed to enable quaternion feature: " + err.Error())
		}

		// Get the BNO08X service from the I2C
		BNO08XService = I2C.GetBNO08XService()

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
				// ralvarezdevbno08x.NewDefaultDebugger(),
				nil,
				ralvarezdevbno08x.DefaultTimeout,
			),
		)
		if err != nil {
			panic("failed to initialize uart rvc bno08x: " + err.Error())
		}
		UARTRVC = uartRVC

		// Set the UART-RVC instance as the BNO08X service
		BNO08XService = uartRVC
	*/
}
