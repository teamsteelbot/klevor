package bno08x

import (
	// bno08x "github.com/ralvarezdev/go-bno08x
	bno08x "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/bno08x/test"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/usbcdc"
)

type (
	// DefaultHandler is the default handler for the BNO08x sensor.
	DefaultHandler struct {
		bno08x                       *bno08x.BNO08X
		usbCDCHandler                internalusbcdc.Handler
		initialQuaternion            *[3]float64
		lastYawDegrees               float64
		accumulatedYawDegrees        float64
		accumulatedYaw90DegreesTurns int
		lastSegmentCount             int
		rollDegrees                  float64
		pitchDegrees                 float64
		yawDegrees                   float64
	}
)

// NewDefaultHandler creates a new DefaultHandler for the BNO08x sensor.
//
// Parameters:
//
// bno08x: The BNO08x sensor instance.
// usbCDCHandler: The USB CDC handler for serial communication.
//
// Returns:
//
// An instance of DefaultHandler, or an error if the BNO08x instance is nil.
func NewDefaultHandler(
	bno08x *bno08x.BNO08X,
	usbCDCHandler internalusbcdc.Handler,
) (*DefaultHandler, error) {
	// Check if the BNO08X instance is nil
	if bno08x == nil {
		return nil, ErrNilBNO08X
	}

	// Check if the USB CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	return &DefaultHandler{
		bno08x,
		usbCDCHandler,
		nil,
		0,
		0,
		0,
		0,
		0,
		0,
		0,
	}, nil
}

// Setup initializes the BNO08X sensor and prepares it for use.
func (h *DefaultHandler) Setup() error {
	// Enable quaternion feature
	if err := h.bno08x.EnableFeature(bno08x.ReportIDRotationVector); err != nil {
		return err
	}

	// Set the initial quaternion values
	h.initialQuaternion = h.bno08x.QuaternionEulerDegrees()
	return nil
}

// Update reads the quaternion data from the BNO08X sensor and updates the roll, pitch, and yaw values.
func (h *DefaultHandler) Update() error {
	// Get the latest quaternion data from the BNO08X sensor in euler degrees
	quaternion := h.bno08x.QuaternionEulerDegrees()
	if quaternion == nil {
		return ErrNilQuaternion
	}

	// Update roll, pitch, and yaw degrees
	h.rollDegrees = quaternion[bno08x.QuaternionRollIndex]
	h.pitchDegrees = quaternion[bno08x.QuaternionPitchIndex]
	h.yawDegrees = quaternion[bno08x.QuaternionYawIndex]

	// Send the yaw degrees message via USB CDC if enabled
	if h.usbCDCHandler != nil {
		if err := h.usbCDCHandler.SendBNO08XYawDegreesMessage(h.yawDegrees); err != nil {
			return err
		}
	}

	// Update internal yaw state
	relativeYawDegrees := h.yawDegrees - h.initialQuaternion[bno08x.QuaternionYawIndex]
	if relativeYawDegrees > 180 {
		relativeYawDegrees -= 360
	} else if relativeYawDegrees < -180 {
		relativeYawDegrees += 360
	}

	// Calculate the change in yaw degrees since the last update
	deltaRawYawDegrees := relativeYawDegrees - h.lastYawDegrees
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
	}

	// If serial communication is enabled, send the turn message
	if h.usbCDCHandler != nil {
		if err := h.usbCDCHandler.SendBNO08XYawTurnsMessage(
			h.accumulatedYaw90DegreesTurns,
		); err != nil {
			return err
		}
	}

	// Update the last yaw degrees
	h.lastYawDegrees = relativeYawDegrees
	return nil
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

// GetAccumulatedYaw90DegreesTurns returns the accumulated yaw in 90 degrees turns.
//
// Returns:
//
// The accumulated yaw in 90 degrees turns.
func (h *DefaultHandler) GetAccumulatedYaw90DegreesTurns() int {
	return h.accumulatedYaw90DegreesTurns
}
