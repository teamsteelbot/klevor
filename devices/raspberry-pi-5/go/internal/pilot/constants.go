package pilot

import (
	"time"
)

var (
	// MinimumValidDistance is the minimum valid distance for the sensors
	MinimumValidDistance = 45.0

	// SetServoAngleAttempts is the number of attempts to set the servo angle
	SetServoAngleAttempts = 3

	// SetMotorSpeedAttempts is the number of attempts to set the motor speed
	SetMotorSpeedAttempts = 3

	// MotorSpeedStartMessageTimeout is the timeout for the motor speed start message
	MotorSpeedStartMessageTimeout = 100 * time.Millisecond

	// ServoAngleStartMessageTimeout is the timeout for the servo angle start message
	ServoAngleStartMessageTimeout = 100 * time.Millisecond

	// MotorSpeedEndMessageTimeout is the timeout for the motor speed end message
	MotorSpeedEndMessageTimeout = 1500 * time.Millisecond

	// ServoAngleEndMessageTimeout is the timeout for the servo angle end message
	ServoAngleEndMessageTimeout = 500 * time.Millisecond

	// RPLiDARDelay is the delay between RPLiDAR scans
	RPLiDARDelay = 100 * time.Millisecond

	// HandlerLoggerProducerTag is the tag for the logger producer
	HandlerLoggerProducerTag = "PILOT_HANDLER"

	// MotorFastPercentage is the percentage of the maximum speed for fast motor speed
	MotorFastPercentage float64 = 0.75

	// MotorNormalPercentage is the percentage of the maximum speed for normal motor speed
	MotorNormalPercentage float64 = 0.625

	// MotorSlowPercentage is the percentage of the maximum speed for slow motor speed
	MotorSlowPercentage float64 = 0.5

	// ServoBigTurnAnglePercentage is the percentage of the maximum angle for big turns
	ServoBigTurnAnglePercentage float64 = 1

	// ServoMediumTurnAnglePercentage is the percentage of the maximum angle for medium turns
	ServoMediumTurnAnglePercentage float64 = 0.75

	// ServoSmallTurnAnglePercentage is the percentage of the maximum angle for small turns
	ServoSmallTurnAnglePercentage float64 = 0.5

	// AlgorithmTurns is the number of turns in the algorithm
	AlgorithmTurns = 12

	// SafetyFrontDistanceStartThreshold is the distance threshold to start safety mode
	SafetyFrontDistanceStartThreshold = 200.0

	// SafetyFrontDistanceStopThreshold is the distance threshold to stop safety mode
	SafetyFrontDistanceStopThreshold = 350.0

	// StopDistanceThreshold is the distance threshold to stop the robot
	StopDistanceThreshold = 1500.0

	// SideDistanceThreshold is the distance threshold for side sensors
	SideDistanceThreshold = 1500.0

	// SideDistanceDifferencePercentage is the percentage difference threshold for side sensors
	SideDistanceDifferencePercentage = 0.15 // 0.2

	// FrontStartTurnDistanceThreshold is the distance threshold to start turning
	FrontStartTurnDistanceThreshold = 600.0 // 500.0

	// FrontStopTurnDistanceThreshold is the distance threshold to stop turning
	FrontStopTurnDistanceThreshold = 1500.0

	// AverageAngleWidth is the width of the angle for average calculations
	AverageAngleWidth = 5
)
