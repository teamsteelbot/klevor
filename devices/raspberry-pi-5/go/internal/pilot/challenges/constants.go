package challenges

import (
	"time"
)

const (
	// ChallengeHandlerLoggerProducerTag is the tag for the challenge handler logger producer
	ChallengeHandlerLoggerProducerTag = "CHALLENGE_HANDLER"

	// GyroscopeTolerance is the tolerance for the gyroscope
	GyroscopeTolerance = 2.0

	// YawDegreesServoAngleRatio is the ratio between yaw degrees and servo angle
	YawDegreesServoAngleRatio = 2.0

	// AverageAngleWidth is the width of the angle for average calculations
	AverageAngleWidth = 3

	// SetServoAngleAttempts is the number of attempts to set the servo angle
	SetServoAngleAttempts = 3

	// SetMotorSpeedAttempts is the number of attempts to set the motor speed
	SetMotorSpeedAttempts = 3

	// MotorSpeedStartMessageTimeout is the timeout for the motor speed start message
	MotorSpeedStartMessageTimeout = 1 * time.Second // 200ms, 500ms

	// ServoAngleStartMessageTimeout is the timeout for the servo angle start message
	ServoAngleStartMessageTimeout = 1 * time.Second

	// MotorSpeedEndMessageTimeout is the timeout for the motor speed end message
	MotorSpeedEndMessageTimeout = 3 * time.Second // 1500 ms, 2000ms

	// ServoAngleEndMessageTimeout is the timeout for the servo angle end message
	ServoAngleEndMessageTimeout = 1 * time.Second // 200 ms, 500ms

	// InitializationDelay is the delay after initialization
	InitializationDelay = 100 * time.Millisecond

	// UpdateDelay is the delay between updates
	UpdateDelay = 10 * time.Millisecond

	// RPLiDARLogInterval is the interval for RPLiDAR logging
	RPLiDARLogInterval = 100 * time.Millisecond

	// CLIPLogInterval is the interval for CLIP logging
	CLIPLogInterval = 100 * time.Millisecond

	// MinTimeBetweenTurns is the minimum time between turns
	MinTimeBetweenTurns = 2 * time.Second

	// MinTimeToCorrectAfterTurn is the minimum time to correct after a turn
	MinTimeToCorrectAfterTurn = 1500 * time.Millisecond

	// MaxDistanceChange is the maximum distance change for safety calculations
	MaxDistanceChange = 100.0

	// MotorBackwardFastPercentage is the percentage of the maximum speed for fast backward motor speed
	MotorBackwardFastPercentage float64 = 1

	// MotorBackwardNormalPercentage is the percentage of the maximum speed for normal backward motor speed
	MotorBackwardNormalPercentage float64 = 0.8

	// MotorBackwardSlowPercentage is the percentage of the maximum speed for slow backward motor speed
	MotorBackwardSlowPercentage float64 = 0.6

	// MotorForwardFastPercentage is the percentage of the maximum speed for fast forward motor speed
	MotorForwardFastPercentage float64 = 1

	// MotorForwardNormalPercentage is the percentage of the maximum speed for normal forward motor speed
	MotorForwardNormalPercentage float64 = 0.8

	// MotorForwardSlowPercentage is the percentage of the maximum speed for slow forward motor speed
	MotorForwardSlowPercentage float64 = 0.6

	// MotorTurningPercentage is the percentage of the maximum speed for turning motor speed
	MotorTurningPercentage float64 = 0.8

	// ServoBigTurnAnglePercentage is the percentage of the maximum angle for big turns
	ServoBigTurnAnglePercentage float64 = 1

	// ServoMediumTurnAnglePercentage is the percentage of the maximum angle for medium turns
	ServoMediumTurnAnglePercentage float64 = 0.66

	// ServoSmallTurnAnglePercentage is the percentage of the maximum angle for small turns
	ServoSmallTurnAnglePercentage float64 = 0.33

	// ServoMediumCorrectionAnglePercentage is the percentage of the maximum angle for medium corrections
	ServoMediumCorrectionAnglePercentage float64 = 0.4

	// ServoSmallCorrectionAnglePercentage is the percentage of the maximum angle for small corrections
	ServoSmallCorrectionAnglePercentage float64 = 0.25

	// Algorithm90DegreeTurns is the number of 90 degree turns in the algorithm
	Algorithm90DegreeTurns uint = 12

	// FrontDistanceChange is the scalar change for the safety front distance calculation
	FrontDistanceChange = 1.25

	// SideDistanceChange is the scalar change for the side distance calculation
	SideDistanceChange = 1.1

	// SafetyFrontDistanceStartThreshold is the distance threshold to start safety mode
	SafetyFrontDistanceStartThreshold = 150.0

	// SafetyFrontDistanceStopThreshold is the distance threshold to stop safety mode
	SafetyFrontDistanceStopThreshold = 325.0

	// StopDistanceThreshold is the distance threshold to stop the robot
	StopDistanceThreshold = 1500.0

	// SideDistanceThreshold is the distance threshold for side sensors
	SideDistanceThreshold = 1750.0

	// SideDistanceMediumDifferencePercentage is the percentage of medium difference threshold for side distances
	SideDistanceMediumDifferencePercentage = 0.35

	// SideDistanceSmallDifferencePercentage is the percentage of small difference threshold for side distances
	SideDistanceSmallDifferencePercentage = 0.15 // 0.2, 0.15, 0.3

	// FrontStartTurnDistanceThreshold is the distance threshold to start turning
	FrontStartTurnDistanceThreshold = 1000.0 // 500.0, 600.0, 650.0, 900.0

	// LaneIdentifierThreshold is used to determine which lane is the robot placed (only used in the closed challenge)
	LaneIdentifierThreshold = 400.0

	// FrontCloseupThreshold is used to move the robot closely to the wall (only used in the closed challenge)
	FrontCloseupThreshold = 100.0

	// CameraRangeThreshold is used to determine if an object is capable of being detected by the camera (only used in the closed challenge)
	CameraRangeThreshold = 250.0

	// ParkingLeaveSideDistanceThreshold is the distance threshold to leave the parking (only used in the closed challenge)
	ParkingLeaveSideDistanceThreshold = 500.0

	// StopBackwardDirectionOnParkingBackwardDistanceThreshold is the distance threshold to stop the backward direction when leaving parking (only used in the closed challenge)
	StopBackwardDirectionOnParkingBackwardDistanceThreshold = 290.0

	// StopForwardDirectionOnParkingFrontDistanceThreshold is the distance threshold to go forward for the first time when leaving parking (only used in the closed challenge)
	StopForwardDirectionOnParkingFrontDistanceThreshold = 95.0

	// LeftParkingSideDistanceThreshold is the distance threshold for the left side sensor when leaving parking (only used in the closed challenge)
	LeftParkingSideDistanceThreshold = 450.0
)
