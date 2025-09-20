package pilot

import (
	"time"
)

var (
	// MinimumValidDistance is the minimum valid distance for the sensors
	MinimumValidDistance = 10.0

	// SetServoAngleAttempts is the number of attempts to set the servo angle
	SetServoAngleAttempts = 3

	// SetMotorSpeedAttempts is the number of attempts to set the motor speed
	SetMotorSpeedAttempts = 3

	// MotorSpeedStartMessageTimeout is the timeout for the motor speed start message
	MotorSpeedStartMessageTimeout = 200 * time.Millisecond

	// ServoAngleStartMessageTimeout is the timeout for the servo angle start message
	ServoAngleStartMessageTimeout = 200 *time.Millisecond

	// MotorSpeedEndMessageTimeout is the timeout for the motor speed end message
	MotorSpeedEndMessageTimeout = 1500 * time.Millisecond

	// ServoAngleEndMessageTimeout is the timeout for the servo angle end message
	ServoAngleEndMessageTimeout = 500 * time.Millisecond

	// RPLiDARDelay is the delay between RPLiDAR scans
	RPLiDARDelay = 100 * time.Millisecond

	// HandlerLoggerProducerTag is the tag for the logger producer
	HandlerLoggerProducerTag = "PILOT_HANDLER"

	// MotorBackwardFastPercentage is the percentage of the maximum speed for fast backward motor speed
	MotorBackwardFastPercentage float64 = 0.5
	
	// MotorBackwardNormalPercentage is the percentage of the maximum speed for normal backward motor speed
	MotorBackwardNormalPercentage float64 = 0.375

	// MotorBackwardSlowPercentage is the percentage of the maximum speed for slow backward motor speed
	MotorBackwardSlowPercentage float64 = 0.25

	// MotorForwardFastPercentage is the percentage of the maximum speed for fast forward motor speed
	MotorForwardFastPercentage float64 = 1.0

	// MotorForwardNormalPercentage is the percentage of the maximum speed for normal forward motor speed
	MotorForwardNormalPercentage float64 = 0.9

	// MotorForwardSlowPercentage is the percentage of the maximum speed for slow forward motor speed
	MotorForwardSlowPercentage float64 = 0.8

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
