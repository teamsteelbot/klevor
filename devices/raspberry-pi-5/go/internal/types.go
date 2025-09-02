package internal

import (
	"fmt"
	"strings"

	ralvarezdevgostringsconvert "github.com/ralvarezdev/go-strings/convert"
)

type (
	// Measure is a struct that represents a single measurement from the RPLiDAR.
	Measure struct {
		angle      float64
		distance   float64
		quality    int
		hasSyncBit bool
	}

	// Classification is the struct for a Hailo CLIP classification
	Classification struct {
		Label      PositiveLabel
		Confidence float32
	}
)

// validateAngle validates the angle value.
//
// Parameters:
//
// angle: Angle value to validate.
// hasSyncBit: Indicates if the measurement has a sync bit.
//
// Returns:
//
// An error if the angle is invalid.
func validateAngle(angle float64, hasSyncBit bool) error {
	// Check if the angle corresponds to a measure with sync bit
	if !hasSyncBit {
		if angle < 0 || angle >= 360 {
			return fmt.Errorf(
				"angle without sync bit must be in [0, 360), got %f",
				angle,
			)
		}
	} else if angle < 0 {
		return fmt.Errorf(
			"angle with sync bit must be non-negative, got %f",
			angle,
		)
	}
	return nil
}

// NewMeasure creates a new Measure instance.
//
// Parameters:
//
// angle: Angle of the measurement in degrees.
// distance: Distance of the measurement in millimeters.
// quality: Quality of the measurement.
// hasSyncBit: Indicates if the measurement has a sync bit.
// isUpsideDown: Indicates if the LIDAR is upside down.
// angleAdjustment: Angle adjustment to apply to the angle.
//
// Returns:
//
// A Measure instance, or an error if any parameter is invalid.
func NewMeasure(
	angle, distance float64,
	quality int,
	hasSyncBit bool,
	isUpsideDown bool,
	angleAdjustment float64,
) (*Measure, error) {
	// Validate angle
	if err := validateAngle(angle, hasSyncBit); err != nil {
		return nil, err
	}

	// Ensure the angle is between 0 and 360 if it has a sync bit
	if hasSyncBit {
		angle = angle - 360.0
	}

	// Adjust angle if the LIDAR is upside down
	if isUpsideDown {
		angle = 360.0 - angle
	}

	// Apply angle adjustment
	if angleAdjustment != 0 {
		angle = angle + angleAdjustment
	}

	// Normalize angle to be within [0, 360)
	if angle < 0 {
		angle = angle + 360.0
	} else if angle >= 360.0 {
		angle = angle - 360.0
	}

	return &Measure{
		angle:      angle,
		distance:   distance,
		quality:    quality,
		hasSyncBit: hasSyncBit,
	}, nil
}

// NewMeasureFromSlamtecC1String creates a new Measure instance from a string representation specific to the Slamtec C1 model.
//
// Parameters:
//
// measureStr: String representation of the measurement.
// isUpsideDown: Indicates if the LIDAR is upside down.
// angleAdjustment: Angle adjustment to apply to the angle.
//
// Returns:
//
// A Measure instance, or an error if the string is invalid.
func NewMeasureFromSlamtecC1String(
	measureStr string,
	isUpsideDown bool,
	angleAdjustment float64,
) (*Measure, error) {
	// Trim and split
	fields := strings.Fields(measureStr)

	// Check if it has sync bit
	hasSyncBit := false
	if len(fields) == 4 && fields[0] == SyncBitCharacter {
		hasSyncBit = true
		fields = fields[1:]
	}

	// Check number of fields
	if len(fields) != 3 {
		return nil, fmt.Errorf("expected 3 fields, got %d", len(fields))
	}

	// Parse fields
	var angle float64
	if err := ralvarezdevgostringsconvert.ToFloat64(
		fields[AngleIndex],
		&angle,
	); err != nil {
		return nil, fmt.Errorf("failed to parse angle: %w", err)
	}

	var distance float64
	if err := ralvarezdevgostringsconvert.ToFloat64(
		fields[DistanceIndex],
		&distance,
	); err != nil {
		return nil, fmt.Errorf("failed to parse distance: %w", err)
	}

	var quality int
	if err := ralvarezdevgostringsconvert.ToInt(
		fields[QualityIndex],
		&quality,
	); err != nil {
		return nil, fmt.Errorf("failed to parse quality: %w", err)
	}

	// Create the Measure instance
	return NewMeasure(
		angle,
		distance,
		quality,
		hasSyncBit,
		isUpsideDown,
		angleAdjustment,
	)
}

// GetAngle returns the angle of the measurement.
//
// Returns:
//
// The angle of the measurement in degrees.
func (m *Measure) GetAngle() float64 {
	return m.angle
}

// GetDistance returns the distance of the measurement.
//
// Returns:
//
// The distance of the measurement in millimeters.
func (m *Measure) GetDistance() float64 {
	return m.distance
}

// GetQuality returns the quality of the measurement.
//
// Returns:
//
// The quality of the measurement.
func (m *Measure) GetQuality() int {
	return m.quality
}

// String returns the string representation of the Measure.
//
// Returns:
//
// The string representation of the Measure.
func (m *Measure) String() string {
	return fmt.Sprintf(
		"%f%s%f%s%d",
		m.angle,
		AttributesSeparator,
		m.distance,
		AttributesSeparator,
		m.quality,
	)
}

// IsRotationCompleted determines if a full rotation has been completed
//
// Returns:
//
// True if a full rotation has been completed, false otherwise.
func (m *Measure) IsRotationCompleted() bool {
	return m.hasSyncBit
}

// NewClassification creates a new Classification instance.
//
// Parameters:
//
// label: The positive label for the classification.
// confidence: The confidence score for the classification.
//
// Returns:
//
// A pointer to a Classification instance or an error if any parameter is invalid.
func NewClassification(
	label PositiveLabel,
	confidence float32,
) (*Classification, error) {
	// Check if the confidence is within the valid range [0.0, 1.0]
	if confidence < 0.0 || confidence > 1.0 {
		return nil, fmt.Errorf(
			"confidence must be in [0.0, 1.0], got %f",
			confidence,
		)
	}

	// Create a new Classification instance
	classification := &Classification{
		Label:      label,
		Confidence: confidence,
	}

	return classification, nil
}

// NewClassificationFromString creates a new Classification instance from a string.
//
// Parameters:
//
// s: The string representation of the classification in the format "label confidence".
//
// Returns:
//
// A pointer to a Classification instance or an error if the string is invalid.
func NewClassificationFromString(s string) (*Classification, error) {
	// Split the string into fields
	fields := strings.Fields(s)
	labelStr := strings.Join(fields[:len(fields)-1], " ")
	confidenceStr := fields[len(fields)-1]

	// Parse the label
	label, err := PositiveLabelFromString(labelStr)
	if err != nil {
		return nil, fmt.Errorf("invalid label: %w", err)
	}

	// Parse the confidence
	var confidence float32
	if err = ralvarezdevgostringsconvert.ToFloat32(
		confidenceStr,
		&confidence,
	); err != nil {
		return nil, fmt.Errorf("failed to parse confidence: %w", err)
	}

	// Create a new Classification instance
	return NewClassification(label, confidence)
}
