//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"encoding/binary"
	"time"

	"machine"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// UARTRVC is a the UART-RVC implementation for the BNO08x sensor.
	UARTRVC struct {
		uartBus       *machine.UART
		txPin         machine.Pin
		rxPin         machine.Pin
		ps0Pin        machine.Pin
		ps1Pin        machine.Pin
		resetPin      machine.Pin
		debugger      Debugger
		timeout       time.Duration
		accelerometer [3]float64
		eulerDegrees  [3]float64
		initComplete  bool
		buffer 	  []byte
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
// ps0Pin: The PS0 pin to set the sensor to UART mode.
// ps1Pin: The PS1 pin to set the sensor to UART mode.
// resetPin: The pin used to reset the BNO08X sensor.
// options: The Options for configuring the BNO08X (optional).
//
// Returns:
//
// An instance of UARTRVC, or an error if the uartBus is nil or configuration fails.
func NewUARTRVC(
	uartBus *machine.UART,
	txPin machine.Pin,
	rxPin machine.Pin,
	ps0Pin machine.Pin,
	ps1Pin machine.Pin,
	resetPin machine.Pin,
	options *UARTRVCOptions,
) (*UARTRVC, tinygotypes.ErrorCode) {
	// Check if the UART bus is nil
	if uartBus == nil {
		return nil, ErrorCodeBNO08XNilUARTBus
	}

	// Set PS0 pin to output and high
	ps0Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps0Pin.High()

	// Set PS1 pin to output and low
	ps1Pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	ps1Pin.Low()

	// Configure UART
	if err := uartBus.Configure(
		machine.UARTConfig{
			BaudRate: UARTRVCBaudRate,
			TX:       txPin,
			RX:       rxPin,
		},
	); err != nil {
		return nil, ErrorCodeBNO08XFailedToConfigureUART
	}

	// If options are nil, initialize with default values
	if options == nil {
		options = NewUARTRVCOptions(nil, UARTRVCTimeout)
	}

	// Get the timeout from options
	timeout := options.Timeout

	// Get the debugger from options
	debugger := options.Options.Debugger

	// Create the UART-RVC instance
	uartRVC := &UARTRVC{
		uartBus:       uartBus,
		txPin:         txPin,
		rxPin:         rxPin,
		ps0Pin:        ps0Pin,
		ps1Pin:        ps1Pin,
		resetPin:      resetPin,
		debugger:      debugger,
		buffer:        make([]byte, UARTRVCPacketLengthBytes),
		timeout:       timeout,
		initComplete:  false,
	}

	// Perform initialization
	if err := uartRVC.Initialize(); err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToInitializeUARTRVC
	}
	return uartRVC, tinygotypes.ErrorCodeNil
}

// Initialize performs the initial setup of the BNO08X sensor, including hardware and software resets.
//
// Returns:
//
// An error if the initialization fails, otherwise nil.
func (u *UARTRVC) Initialize() tinygotypes.ErrorCode {
	// Check if already initialized
	if u.initComplete {
		return tinygotypes.ErrorCodeNil
	}

	// Log initialization start
	if u.debugger != nil {
		u.debugger.Debug("Initializing BNO08X sensor with UART-RVC...")
	}

	// Perform reset
	u.Reset()
	u.initComplete = true

	// Log
	if u.debugger != nil {
		u.debugger.Debug("BNO08X sensor with UART-RVC initialized successfully.")
	}
	return tinygotypes.ErrorCodeNil
}

// HardwareReset performs a hardware reset of the BNO08X sensor using the specified reset pin.
//
// Returns:
//
// An error if the reset process fails, otherwise nil.
func (u *UARTRVC) HardwareReset() {
	HardwareReset(u.resetPin, u.debugger, nil)
}

// SoftwareReset performs a software reset of the BNO08X sensor.
//
// Returns:
//
// An error if the software reset fails, otherwise nil.
func (u *UARTRVC) SoftwareReset() tinygotypes.ErrorCode {
	return tinygotypes.ErrorCodeNil
}

// Reset performs a reset of the BNO08X sensor.
//
// Returns:
//
// An error if the reset fails, otherwise nil.
func (u *UARTRVC) Reset() tinygotypes.ErrorCode {
	// Perform hardware reset
	u.HardwareReset()

	// Perform software reset
	return u.SoftwareReset()
}

// ParseFrame parses a heading frame from the BNO08x RVC.
//
// Returns:
//
// An error if parsing fails.
func (u *UARTRVC) ParseFrame() tinygotypes.ErrorCode {
	// Retrieve and parse fields from the frame
	// index := u.buffer[2]
	yaw := int16(binary.LittleEndian.Uint16(u.buffer[3:5]))
	pitch := int16(binary.LittleEndian.Uint16(u.buffer[5:7]))
	roll := int16(binary.LittleEndian.Uint16(u.buffer[7:9]))
	xAccel := int16(binary.LittleEndian.Uint16(u.buffer[9:11]))
	yAccel := int16(binary.LittleEndian.Uint16(u.buffer[11:13]))
	zAccel := int16(binary.LittleEndian.Uint16(u.buffer[13:15]))
	// res1 := u.buffer[15]
	// res2 := u.buffer[16]
	// res3 := u.buffer[17]
	checksum := u.buffer[18]

	// Validate checksum
	checksumCalc := byte(0)
	for i := UARTRVCHeaderLength; i < UARTRVCPacketLengthBytes-1; i++ {
		checksumCalc += u.buffer[i]
	}
	if checksumCalc != checksum {
		if u.debugger != nil {
			u.debugger.Debug("invalid checksum")
		}
		return ErrorCodeBNO08XUARTRVCInvalidChecksum
	}

	// Update the current euler degrees
	u.eulerDegrees[EulerDegreesYawIndex] = float64(yaw) * 0.01
	u.eulerDegrees[EulerDegreesPitchIndex] = float64(pitch) * 0.01
	u.eulerDegrees[EulerDegreesRollIndex] = float64(roll) * 0.01

	// Update the current accelerometer values
	u.accelerometer[ThreeDimensionalXIndex] = float64(xAccel) * MilligToMeterPerSecondSquared
	u.accelerometer[ThreeDimensionalYIndex] = float64(yAccel) * MilligToMeterPerSecondSquared
	u.accelerometer[ThreeDimensionalZIndex] = float64(zAccel) * MilligToMeterPerSecondSquared
	return tinygotypes.ErrorCodeNil
}

// readByte blocks until a byte is read (simple poll).
//
// Returns:
//
// A byte read from UART and an error if any.
func (u *UARTRVC) readByte() (byte, tinygotypes.ErrorCode) {
	startTime := time.Now()
	for time.Since(startTime) < UARTByteTimeout {
		if u.uartBus.Buffered() > 0 {
			if b, err := u.uartBus.ReadByte(); err == nil {
				return b, tinygotypes.ErrorCodeNil
			}
			return 0, ErrorCodeBNO08XUARTRVCFailedToReadByte
		}
		time.Sleep(NoByteDelay)
	}
	return 0, ErrorCodeBNO08XUARTRVCByteTimeout
}

// Read reads a heading frame from the BNO08x from UART-RVC.
//
// Returns:
//
// An error if reading fails or times out.
func (u *UARTRVC) Read() tinygotypes.ErrorCode {
	// Clear frame buffer
	for i := range u.buffer {
		u.buffer[i] = 0
	}

	// Get the start time for timeout calculation
	start := time.Now()
	for time.Since(start) < u.timeout {
		// Loop until timeout to find the start bytes
		processedBytes := 0
		for processedBytes < UARTRVCHeaderLength {
			b, err := u.readByte()
			if err != tinygotypes.ErrorCodeNil {
				return err
			}
			u.buffer[processedBytes] = b
			processedBytes++
		}

		// Check if we have the start bytes
		if u.buffer[0] != UARTRVCStartByte || u.buffer[1] != UARTRVCStartByte {
			// Check if we have the first start byte
			if u.buffer[1] == UARTRVCStartByte {
				// Shift the second byte to the first position
				u.buffer[0] = u.buffer[1]
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
			if err != tinygotypes.ErrorCodeNil {
				return err
			}
			u.buffer[processedBytes] = b
			processedBytes++
		}

		// Print the raw frame for debugging
		if u.debugger != nil {
			u.debugger.Debug("Received frame")
		}

		// Parse the frame
		if err := u.ParseFrame(); err != tinygotypes.ErrorCodeNil {
			if u.debugger != nil {
				u.debugger.Debug("Failed to parse frame")
			}
			return ErrorCodeBNO08XFailedToParseFrame
		}
		return tinygotypes.ErrorCodeNil
	}
	return ErrorCodeBNO08XUARTRVCUARTTimeout
}

// Update reads a new frame from the BNO08x sensor and updates the internal state.
//
// Returns:
//
// An error if reading or parsing the frame fails.
func (u *UARTRVC) Update() tinygotypes.ErrorCode {
	return u.Read()
}

// GetAcceleration returns the acceleration measurements on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the acceleration values.
func (u *UARTRVC) GetAcceleration() [3]float64 {
	return u.accelerometer
}

// GetEulerDegrees returns the current rotation vector as Euler angles in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees.
func (u *UARTRVC) GetEulerDegrees() [3]float64 {
	return u.eulerDegrees
}
