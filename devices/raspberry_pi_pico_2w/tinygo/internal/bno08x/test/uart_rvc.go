//go:build tinygo && (rp2040 || rp2350)

package test

import (
	"encoding/binary"
	"fmt"
	"time"

	"machine"
)

type (
	// UARTRVC is a the UART-RVC implementation for the BNO08x sensor.
	UARTRVC struct {
		uartBus       *machine.UART
		txPin         machine.Pin
		rxPin         machine.Pin
		ps0           machine.Pin
		ps1           machine.Pin
		resetPin      machine.Pin
		dataBuffer    DataBuffer
		debugger      Debugger
		timeout       time.Duration
		accelerometer *[3]float64
		eulerDegrees  *[3]float64
	}

	// UARTRVCOptions struct for configuring the BNO08X over UART-RVC.
	UARTRVCOptions struct {
		Options *Options
		Timeout time.Duration
	}
)

// NewUARTRVCOptions creates a new UARTRVCOptions instance with default values.
//
// Parameters:
//
// debugger: The debugger to use for logging and debugging information (optional).
// timeout: The timeout duration for reading data (optional).
//
// Returns:
//
// A pointer to a new UARTRVCOptions instance.
func NewUARTRVCOptions(
	debugger Debugger,
	timeout time.Duration,
) *UARTRVCOptions {
	return &UARTRVCOptions{
		Options: NewOptions(debugger),
		Timeout: timeout,
	}
}

// NewUARTRVC creates a new UARTRVC instance.
//
// Parameters:
//
// uartBus: The UART bus to use for communication.
// txPin: The TX pin for UART communication.
// rxPin: The RX pin for UART communication.
// ps0: The PS0 pin to set the sensor to UART mode.
// ps1: The PS1 pin to set the sensor to UART mode.
// resetPin: The pin used to reset the BNO08X sensor.
// dataBuffer: The data buffer to use for storing Packet data.
// options: The Options for configuring the BNO08X (optional).
//
// Returns:
//
// An instance of UARTRVC, or an error if the uartBus is nil or configuration fails.
func NewUARTRVC(
	uartBus *machine.UART,
	txPin machine.Pin,
	rxPin machine.Pin,
	ps0 machine.Pin,
	ps1 machine.Pin,
	resetPin machine.Pin,
	dataBuffer DataBuffer,
	options *Options,
) (*UARTRVC, error) {
	// Check if the UART bus is nil
	if uartBus == nil {
		return nil, ErrNilUARTBus
	}

	// Set PS0 pin to output and high
	ps0.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps0.High()

	// Set PS1 pin to output and low
	ps1.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps1.Low()

	// Configure UART
	if err := uartBus.Configure(
		machine.UARTConfig{
			BaudRate: UARTRVCBaudRate,
			TX:       txPin,
			RX:       rxPin,
		},
	); err != nil {
		return nil, fmt.Errorf("failed to configure uart: %w", err)
	}

	// If options are nil, initialize with default values
	if options == nil {
		options = NewUARTRVCOptions(nil, DefaultTimeout)
	}

	// Get the timeout from options or use default
	timeout := options.Timeout
	if timeout == nil {
		defaultTimeout := DefaultUARTRVCTimeout
		timeout = &defaultTimeout
	}

	// Get the debugger from options
	debugger := options.Options.Debugger

	return &UARTRVC{
		uartBus:       uartBus,
		txPin:         txPin,
		rxPin:         rxPin,
		ps0:           ps0,
		ps1:           ps1,
		resetPin:      resetPin,
		dataBuffer:    dataBuffer,
		debugger:      debugger,
		accelerometer: &InitialBnoSensorReportThreeDimensional,
		eulerDegrees:  &InitialBnoSensorReportThreeDimensional,
	}, nil
}

// ParseFrame parses a heading frame from the BNO08x RVC.
//
// Parameters:
//
// frame: A pointer to a byte slice containing the frame data.
//
// Returns:
//
// An error if the frame is nil or invalid.
func (u *UARTRVC) ParseFrame(frame *[]byte) error {
	// Check if the frame is nil
	if frame == nil {
		return ErrNilFrame
	}

	// Check if the frame length is at least 17 bytes
	if len(*frame) < 17 {
		return ErrFrameTooShort
	}

	// Retrieve and parse fields from the frame
	// index := frame[0]
	yaw := int16(binary.LittleEndian.Uint16((*frame)[1:3]))
	pitch := int16(binary.LittleEndian.Uint16((*frame)[3:5]))
	roll := int16(binary.LittleEndian.Uint16((*frame)[5:7]))
	xAccel := int16(binary.LittleEndian.Uint16((*frame)[7:9]))
	yAccel := int16(binary.LittleEndian.Uint16((*frame)[9:11]))
	zAccel := int16(binary.LittleEndian.Uint16((*frame)[11:13]))
	// res1 := (*frame)[13]
	// res2 := (*frame)[14]
	// res3 := (*frame)[15]
	checksum := (*frame)[16]

	// Validate checksum
	checksumCalc := byte(0)
	for i := 0; i < 16; i++ {
		checksumCalc += (*frame)[i]
	}
	if checksumCalc != checksum {
		return ErrInvalidChecksum
	}

	// Update the current euler degrees
	u.eulerDegrees[EulerDegreesYawIndex] = float64(yaw) * 0.01
	u.eulerDegrees[EulerDegreesPitchIndex] = float64(pitch) * 0.01
	u.eulerDegrees[EulerDegreesRollIndex] = float64(roll) * 0.01

	// Update the current accelerometer values
	u.accelerometer[ThreeDimensionalXIndex] = float64(xAccel) * MilligToMeterPerSecondSquared
	u.accelerometer[ThreeDimensionalYIndex] = float64(yAccel) * MilligToMeterPerSecondSquared
	u.accelerometer[ThreeDimensionalZIndex] = float64(zAccel) * MilligToMeterPerSecondSquared
	return nil
}

// readByte blocks until a byte is read (simple poll).
//
// Returns:
//
// A byte read from UART and an error if any.
func (u *UARTRVC) readByte() (byte, error) {
	startTime := time.Now()
	for time.Since(startTime) < UARTByteTimeout {
		if pr.uartBus.Buffered() > 0 {
			return pr.uartBus.ReadByte()
		}
		time.Sleep(1 * time.Millisecond)
	}
	return 0, ErrUARTTimeout
}

// Read reads a heading frame from the BNO08x from UART-RVC.
//
// Returns:
//
// An error if reading fails or times out.
func (u *UARTRVC) Read() error {
	// Get the start time for timeout calculation
	start := time.Now()
	frame := make([]byte, UARTRVCPacketLengthBytes)

	for time.Since(start) < u.timeout {
		// Loop until timeout to find the start bytes
		processedBytes := 0
		for procesedBytes < UARTRVCHeaderLengthBytes {
			b, err := u.readByte()
			if err != nil {
				return nil, err
			}
			frame[processedBytes] = b
			processedBytes++
		}

		// Check if we have the start bytes
		if frame[0] != UARTRVCStartByte || frame[1] != UARTRVCStartByte {
			// Check if we have the first start byte
			if frame[1] == UARTRVCStartByte {
				// Shift the second byte to the first position
				frame[0] = frame[1]
				processedBytes = 1
			} else {
				// Reset processed bytes
				processedBytes = 0
			}
			continue
		}

		// We have the start bytes, read the rest of the frame
		for processedBytes < UARTRVCPacketLengthBytes {
			b, err := u.readByte()
			if err != nil {
				return nil, err
			}
			frame[processedBytes] = b
			processedBytes++
		}

		// Parse the frame
		if err := u.ParseFrame(&frame); err != nil {
			// If parsing fails, log the error and try again
			if u.debugger != nil {
				u.debugger.Debug(fmt.Sprintf("failed to parse frame: %v", err))
			}
			return err
		}
		return nil
	}
	return ErrTimeout
}

// Acceleration returns the acceleration measurements on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the acceleration values.
func (u *UARTRVC) Acceleration() *[3]float64 {
	return u.accelerometer
}

// EulerDegrees returns the current rotation vector as Euler angles in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees.
func (u *UARTRVC) EulerDegrees() *[3]float64 {
	return u.eulerDegrees
}
