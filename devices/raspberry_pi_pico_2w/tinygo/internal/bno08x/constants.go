package bno08x

import (
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

	// I2C is the I2C instance for the BNO08x sensor.
	// I2C *bno08x.I2C

	// UART is the UART instance for the BNO08x sensor.
	UART *bno08x.UART

	// BNO08XHandler is the handler for the BNO08x sensor.
	BNO08XHandler *DefaultHandler
)

func init() {
	/*
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
			bno08x.NewI2COptions(bno08x.NewDefaultDebugger(), &address0),
		)
		if err != nil {
			panic("failed to initialize i2c bno08x: " + err.Error())
		}
		I2C = i2c

		// Initialize the BNO08x handler with default settings.
		bno08xHandler, err := NewDefaultHandler(
			&I2C.BNO08X,
			internalusbcdc.USBCDCHandler,
		)
		if err != nil {
			panic("failed to initialize bno08x handler: " + err.Error())
		}
		BNO08XHandler = bno08xHandler
	*/

	// Initialize the BNO08x UART instance with default settings.
	uart, err := bno08x.NewUART(
		machine.UART1,
		machine.GPIO8,
		machine.GPIO9,
		machine.GPIO6,
		machine.GPIO7,
		machine.GPIO4,
		DataBuffer,
		bno08x.NewUARTOptions(bno08x.NewDefaultDebugger(), true),
		// bno08x.NewUARTOptions(nil, false),
	)
	if err != nil {
		panic("failed to initialize uart bno08x: " + err.Error())
	}
	UART = uart

	// Initialize the BNO08x handler with default settings.
	bno08xHandler, err := NewDefaultHandler(
		&UART.BNO08X,
		internalusbcdc.USBCDCHandler,
	)
	if err != nil {
		panic("failed to initialize bno08x handler: " + err.Error())
	}
	BNO08XHandler = bno08xHandler

	// Call the setup function to initialize the sensor
	if err = BNO08XHandler.Setup(); err != nil {
		panic("failed to setup bno08x: " + err.Error())
	}
}
