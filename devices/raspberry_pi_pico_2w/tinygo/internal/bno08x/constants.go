package bno08x

import (
	"time"

	"machine"

	// bno08x "github.com/ralvarezdev/go-adafruit-bno08x"
	bno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

const (
	// MaxCalibrationDuration is the maximum duration for calibration of the BNO08x sensor.
	MaxCalibrationDuration = 5 * time.Second

	// MaxCalibrationAttempts is the maximum number of attempts to calibrate the BNO08x sensor.
	MaxCalibrationAttempts = 10
)

var (
	// DataBuffer is the default data buffer size for the BNO08x sensor.
	DataBuffer = bno08x.NewDefaultDataBuffer()

	// I2C is the I2C instance for the BNO08x sensor.
	I2C *bno08x.I2C

	// BNO08XHandler is the handler for the BNO08x sensor.
	BNO08XHandler *DefaultHandler
)

func init() {
	// Initialize the BNO08x I2C instance with default settings.
	i2c, err := bno08x.NewI2C(
		machine.I2C1,
		machine.GPIO26,
		machine.GPIO27,
		bno08x.I2CDefaultAddress,
		DataBuffer,
		bno08x.NewOptions(bno08x.NewDefaultDebugger(), nil),
	)
	if err != nil {
		panic("failed to initialize bno08x: " + err.Error())
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

	// Call the setup function to initialize the sensor
	if err = BNO08XHandler.Setup(); err != nil {
		panic("failed to setup bno08x: " + err.Error())
	}
}
