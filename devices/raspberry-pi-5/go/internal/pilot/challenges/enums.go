package challenges

type (
	// ServoDirection is an enum to represent the different servo directions for the vehicle.
	ServoDirection uint8

	// MotorDirection is an enum to represent the different motor directions for the vehicle.
	MotorDirection uint8
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
