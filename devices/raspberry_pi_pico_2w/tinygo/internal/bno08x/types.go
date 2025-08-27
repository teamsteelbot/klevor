package bno08x

import (
	ralvarezdevbno08x "github.com/ralvarezdev/go-bno08x"
	internalledonboard "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/led/onboard"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

type (
	// DefaultHandler is the default handler for the BNO08x sensor.
	DefaultHandler struct {
		bno08xService                ralvarezdevbno08x.BNO08XService
		usbCDCHandler                internalusbcdc.Handler
		initialEulerDegrees          *[3]float64
		lastYawDegrees               float64
		lastRelativeYawDegrees       float64
		accumulatedYawDegrees        float64
		accumulatedYaw90DegreesTurns int
		lastSegmentCount             int
		eulerDegrees                 *[3]float64
		rollDegrees                  float64
		pitchDegrees                 float64
		yawDegrees                   float64
	}
)

// NewDefaultHandler creates a new DefaultHandler for the BNO08x sensor.
//
// Parameters:
//
// bno08xService: The BNO08x sensor instance.
// usbCDCHandler: The USB CDC handler for serial communication.
//
// Returns:
//
// An instance of DefaultHandler, or an error if the BNO08x instance is nil.
func NewDefaultHandler(
	bno08xService ralvarezdevbno08x.BNO08XService,
	usbCDCHandler internalusbcdc.Handler,
) (*DefaultHandler, error) {
	// Check if the BNO08X service is nil
	if bno08xService == nil {
		return nil, ralvarezdevbno08x.ErrNilBNO08XService
	}

	// Check if the USB CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	return &DefaultHandler{
		bno08xService,
		usbCDCHandler,
		nil,
		0,
		0,
		0,
		0,
		0,
		nil,
		0,
		0,
		0,
	}, nil
}

// Update reads the euler degrees data from the BNO08X sensor and updates
//
// Returns:
//
// An error if reading from the sensor or sending messages fails
func (h *DefaultHandler) Update() error {
	// Turn on the LED
	internalledonboard.OnBoardHandler.SetOn()

	// Get the latest euler degrees from the BNO08X sensor
	eulerDegrees := h.bno08xService.GetEulerDegrees()
	if eulerDegrees == nil {
		return ralvarezdevbno08x.ErrNilEulerDegrees
	}

	// Turn off the LED
	internalledonboard.OnBoardHandler.SetOff()

	// Update roll, pitch, and yaw degrees
	h.lastYawDegrees = h.yawDegrees
	h.eulerDegrees = eulerDegrees
	h.rollDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesRollIndex]
	h.pitchDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesPitchIndex]
	h.yawDegrees = eulerDegrees[ralvarezdevbno08x.EulerDegreesYawIndex]

	// Send the yaw degrees message via USB CDC if enabled
	if h.usbCDCHandler != nil {
		// Only send if the yaw has changed significantly
		hasChanged := false
		if h.yawDegrees > h.lastYawDegrees && h.yawDegrees > h.lastYawDegrees+YawDegreesDifference {
			hasChanged = true
		} else if h.yawDegrees < h.lastYawDegrees && h.yawDegrees < h.lastYawDegrees-YawDegreesDifference {
			hasChanged = true
		}

		// Send the yaw degrees message if it has changed
		if hasChanged {
			if err := h.usbCDCHandler.SendBNO08XYawDegreesMessage(h.yawDegrees); err != nil {
				return err
			}
		}
	}

	// Update internal yaw state
	relativeYawDegrees := h.yawDegrees - h.initialEulerDegrees[ralvarezdevbno08x.EulerDegreesYawIndex]
	if relativeYawDegrees > 180 {
		relativeYawDegrees -= 360
	} else if relativeYawDegrees < -180 {
		relativeYawDegrees += 360
	}

	// Calculate the change in yaw degrees since the last update
	deltaRawYawDegrees := relativeYawDegrees - h.lastRelativeYawDegrees
	if deltaRawYawDegrees > 180 {
		deltaRawYawDegrees -= 360
	} else if deltaRawYawDegrees < -180 {
		deltaRawYawDegrees += 360
	}

	// Update accumulated yaw and segment count
	h.accumulatedYawDegrees += deltaRawYawDegrees
	currentSegmentCount := int(h.accumulatedYawDegrees / 90)
	if currentSegmentCount != h.lastSegmentCount {
		h.accumulatedYaw90DegreesTurns += currentSegmentCount - h.lastSegmentCount
		h.lastSegmentCount = currentSegmentCount

		// If serial communication is enabled, send the turn message
		if h.usbCDCHandler != nil {
			if err := h.usbCDCHandler.SendBNO08XYawTurnsMessage(
				h.accumulatedYaw90DegreesTurns,
			); err != nil {
				return err
			}
		}
	}

	// Update the last yaw degrees
	h.lastRelativeYawDegrees = relativeYawDegrees
	return nil
}

// Initialize initializes the BNO08X sensor.
//
// Returns:
//
// An error if the initialization fails
func (h *DefaultHandler) Initialize() error {
	return h.bno08xService.Initialize()
}

// HardwareReset performs a hardware reset of the BNO08X sensor.
func (h *DefaultHandler) HardwareReset() {
	h.bno08xService.HardwareReset()
}

// SoftwareReset performs a software reset of the BNO08X sensor.
//
// Returns:
//
// An error if the software reset fails
func (h *DefaultHandler) SoftwareReset() error {
	return h.bno08xService.SoftwareReset()
}

// Reset performs a reset of the BNO08X sensor.
//
// Returns:
//
// An error if the reset fails
func (h *DefaultHandler) Reset() error {
	return h.bno08xService.Reset()
}

// SetInitialEulerDegrees sets initial euler degrees as reference
//
// Parameters:
//
// eulerDegrees: The initial euler degrees to set as reference. If nil, the current
// roll, pitch, and yaw degrees will be used as the initial reference.
func (h *DefaultHandler) SetInitialEulerDegrees(eulerDegrees *[3]float64) {
	if eulerDegrees != nil {
		h.initialEulerDegrees = eulerDegrees
	} else {
		h.initialEulerDegrees = h.eulerDegrees
	}
}

// GetRollDegrees returns the roll angle in degrees.
//
// Returns:
//
// The roll angle in degrees.
func (h *DefaultHandler) GetRollDegrees() float64 {
	return h.rollDegrees
}

// GetPitchDegrees returns the pitch angle in degrees.
//
// Returns:
//
// The pitch angle in degrees.
func (h *DefaultHandler) GetPitchDegrees() float64 {
	return h.pitchDegrees
}

// GetYawDegrees returns the yaw angle in degrees.
//
// Returns:
//
// The yaw angle in degrees.
func (h *DefaultHandler) GetYawDegrees() float64 {
	return h.yawDegrees
}

// GetEulerDegrees returns the roll, pitch, and yaw angles in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees.
func (h *DefaultHandler) GetEulerDegrees() *[3]float64 {
	return h.eulerDegrees
}

// GetAccumulatedYaw90DegreesTurns returns the accumulated yaw in 90 degrees turns.
//
// Returns:
//
// The accumulated yaw in 90 degrees turns.
func (h *DefaultHandler) GetAccumulatedYaw90DegreesTurns() int {
	return h.accumulatedYaw90DegreesTurns
}
