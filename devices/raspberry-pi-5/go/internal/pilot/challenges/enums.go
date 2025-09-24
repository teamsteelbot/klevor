package challenges

import (
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

type (
	// ServoDirection is an enum to represent the different servo directions for the vehicle.
	ServoDirection uint8

	// MotorDirection is an enum to represent the different motor directions for the vehicle.
	MotorDirection uint8

	// ObjectDetectionDirection is an enum to represent the different object detection directions for the vehicle.
	ObjectDetectionDirection uint8
)

const (
	ServoDirectionNil ServoDirection = iota
	ServoDirectionLeft
	ServoDirectionRight
	ServoDirectionStraight
)

const (
	MotorDirectionNil MotorDirection = iota
	MotorDirectionForward
	MotorDirectionBackward
	MotorDirectionStop
)

const (
	ObjectDetectionDirectionNil ObjectDetectionDirection = iota
	ObjectDetectionDirectionLeft
	ObjectDetectionDirectionRight
	ObjectDetectionDirectionFront
)

var (
	// ServoDirectionNames maps a given ServoDirection to its string name
	ServoDirectionNames = map[ServoDirection]string{
		ServoDirectionLeft:     "left",
		ServoDirectionRight:    "right",
		ServoDirectionStraight: "straight",
	}

	// MotorDirectionNames maps a given MotorDirection to its string name
	MotorDirectionNames = map[MotorDirection]string{
		MotorDirectionForward:  "forward",
		MotorDirectionBackward: "backward",
		MotorDirectionStop:     "stop",
	}

	// ObjectDetectionDirectionNames maps a given ObjectDetectionDirection to its string name
	ObjectDetectionDirectionNames = map[ObjectDetectionDirection]string{
		ObjectDetectionDirectionLeft:  "left",
		ObjectDetectionDirectionRight: "right",
		ObjectDetectionDirectionFront: "front",
	}
)

// String returns the string representation of the ServoDirection
//
// Returns:
//
// The string representation of the ServoDirection enum
func (r ServoDirection) String() string {
	return ServoDirectionNames[r]
}

// String returns the string representation of the MotorDirection
//
// Returns:
//
// The string representation of the MotorDirection enum
func (r MotorDirection) String() string {
	return MotorDirectionNames[r]
}

// CardinalDirection returns the corresponding CardinalDirection for the given ServoDirection
//
// Returns:
//
// The corresponding CardinalDirection for the given ServoDirection
func (r ServoDirection) CardinalDirection() gorplidarsdkhandler.CardinalDirection {
	switch r {
	case ServoDirectionLeft:
		return gorplidarsdkhandler.CardinalDirectionWest
	case ServoDirectionRight:
		return gorplidarsdkhandler.CardinalDirectionEast
	case ServoDirectionStraight:
		return gorplidarsdkhandler.CardinalDirectionNorth
	default:
		return gorplidarsdkhandler.CardinalDirectionNil
	}
}

// OppositeCardinalDirection returns the opposite CardinalDirection for the given ServoDirection
//
// Returns:
//
// The opposite CardinalDirection for the given ServoDirection
func (r ServoDirection) OppositeCardinalDirection() gorplidarsdkhandler.CardinalDirection {
	switch r {
	case ServoDirectionLeft:
		return gorplidarsdkhandler.CardinalDirectionEast
	case ServoDirectionRight:
		return gorplidarsdkhandler.CardinalDirectionWest
	case ServoDirectionStraight:
		return gorplidarsdkhandler.CardinalDirectionSouth
	default:
		return gorplidarsdkhandler.CardinalDirectionNil
	}
}

// Opposite returns the opposite ServoDirection
//
// Returns:
//
// The opposite ServoDirection
func (r ServoDirection) Opposite() ServoDirection {
	switch r {
	case ServoDirectionLeft:
		return ServoDirectionRight
	case ServoDirectionRight:
		return ServoDirectionLeft
	case ServoDirectionStraight:
		return ServoDirectionStraight
	default:
		return ServoDirectionNil
	}
}

// String returns the string representation of the ObjectDetectionDirection
//
// Returns:
//
// The string representation of the ObjectDetectionDirection enum
func (r ObjectDetectionDirection) String() string {
	return ObjectDetectionDirectionNames[r]
}

// ObjectDetectionDirectionFromCardinalDirection returns the corresponding ObjectDetectionDirection for the given CardinalDirection
//
// Parameters:
//
// cardinalDirection: The CardinalDirection to convert
//
// Returns:
//
// The corresponding ObjectDetectionDirection for the given CardinalDirection
func ObjectDetectionDirectionFromCardinalDirection(cardinalDirection gorplidarsdkhandler.CardinalDirection) ObjectDetectionDirection {
	// Check if the cardinal direction is nil
	if cardinalDirection == gorplidarsdkhandler.CardinalDirectionNil {
		return ObjectDetectionDirectionNil
	}

	// Check if the cardinal direction is in the left directions
	for _, leftDirection := range ObjectDetectionLeftCardinalDirections {
		if cardinalDirection == leftDirection {
			return ObjectDetectionDirectionLeft
		}
	}

	// Check if the cardinal direction is in the right directions
	for _, rightDirection := range ObjectDetectionRightCardinalDirections {
		if cardinalDirection == rightDirection {
			return ObjectDetectionDirectionRight
		}
	}

	// Check if the cardinal direction is in the front directions
	for _, frontDirection := range ObjectDetectionFrontCardinalDirections {
		if cardinalDirection == frontDirection {
			return ObjectDetectionDirectionFront
		}
	}
	return ObjectDetectionDirectionNil
}
