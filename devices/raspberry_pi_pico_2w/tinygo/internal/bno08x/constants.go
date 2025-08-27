package bno08x

import (
	"time"

	"machine"

	// bno08x "github.com/ralvarezdev/go-bno08x"
	bno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

var (
	// DataBuffer is the default data buffer size for the BNO08x sensor.
	DataBuffer = bno08x.NewDefaultDataBuffer()

	// YawDegreesDifference is the difference in degrees to consider a yaw change.
	YawDegreesDifference = 1.0

	// ResetBNO08XInterval is the interval to reset the BNO08x sensor to prevent overflow.
	ResetBNO08XInterval = 30 * time.Second

	// BNO08X is the BNO08x sensor instance.
	BNO08X *bno08x.BNO08X

	// BNO08XService is the BNO08x service.
	BNO08XService bno08x.BNO08XService

	// I2C is the I2C instance for the BNO08x sensor.
	// I2C *bno08x.I2C

	// UART is the UART instance for the BNO08x sensor.
	UART *bno08x.UART

	// UARTRVC is the UART-RVC instance for the BNO08x sensor.
	// UARTRVC *bno08x.UARTRVC

	// BNO08XHandler is the handler for the BNO08x sensor.
	BNO08XHandler *DefaultHandler
)

func init() {
	/*
		// ----- I2C Instance -----

		// Initialize the BNO08x I2C instance with default settings.
		address0 := machine.GPIO28
		i2c, err := bno08x.NewI2C(
			machine.I2C1,
			machine.GPIO26,
			machine.GPIO27,
			bno08x.I2CAlternativeAddress,
			machine.GPIO6,
			machine.GPIO7,
			machine.GPIO4,
			DataBuffer,
			afterReset,
			bno08x.NewI2COptions(bno08x.NewDefaultDebugger(), &address0),
		)
		if err != nil {
			panic("failed to initialize i2c bno08x: " + err.Error())
		}
		I2C = i2c

		// Enable quaternion feature
		if err = I2C.EnableFeature(bno08x.ReportIDRotationVector); err != nil {
			panic("failed to enable quaternion feature: " + err.Error())
		}

		// Get the BNO08X instance and service from the I2C
		BNO08X = I2C.GetBNO08X()
		BNO08XService = I2C.GetBNO08XService()
	*/

	// ----- UART Instance -----

	// Initialize the BNO08x UART instance with default settings.
	uart, err := bno08x.NewUART(
		machine.UART1,
		machine.GPIO8,
		machine.GPIO9,
		machine.GPIO6,
		machine.GPIO7,
		machine.GPIO4,
		DataBuffer,
		afterReset,
		// bno08x.NewUARTOptions(bno08x.NewDefaultDebugger(), true),
		bno08x.NewUARTOptions(nil, false),
	)
	if err != nil {
		panic("failed to initialize uart bno08x: " + err.Error())
	}
	UART = uart

	// Get the BNO08X instance and service from the UART
	BNO08X = UART.GetBNO08X()
	BNO08XService = UART.GetBNO08XService()

	/*
		// ----- UART-RVC Instance -----

		// Initialize the BNO08x UART-RVC instance with default settings.
		uartRVC, err := bno08x.NewUARTRVC(
			machine.UART1,
			machine.GPIO8,
			machine.GPIO9,
			machine.GPIO6,
			machine.GPIO7,
			machine.GPIO4,
			DataBuffer,
			bno08x.NewUARTRVCOptions(
				// bno08x.NewDefaultDebugger(),
				nil,
				bno08x.DefaultTimeout,
			),
		)
		if err != nil {
			panic("failed to initialize uart rvc bno08x: " + err.Error())
		}
		UARTRVC = uartRVC

		// Set the UART-RVC instance as the BNO08X service
		BNO08XService = uartRVC
	*/

	// ----- All Instances -----

	// Initialize the BNO08x handler with default settings.
	bno08xHandler, err := NewDefaultHandler(
		BNO08XService,
		internalusbcdc.USBCDCHandler,
	)
	if err != nil {
		panic("failed to initialize bno08x handler: " + err.Error())
	}
	BNO08XHandler = bno08xHandler

	// Set the initial euler degrees to BNO08X handler
	BNO08XHandler.SetInitialEulerDegrees(BNO08XService.GetEulerDegrees())
}
