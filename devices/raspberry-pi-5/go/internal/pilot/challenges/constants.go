package challenges

import (
	"time"
)

const (
	// ServiceLoggerProducerTag is the tag for the service logger producer
	ServiceLoggerProducerTag = "CHALLENGE_SERVICE"

	// ChallengeHandlerLoggerProducerTag is the tag for the challenge handler logger producer
	ChallengeHandlerLoggerProducerTag = "CHALLENGE_HANDLER"

	// Algorithm90DegreeTurns is the number of 90 degree turns in the algorithm
	Algorithm90DegreeTurns uint = 12

	// MinTimeBetweenTurns is the minimum time between turns
	MinTimeBetweenTurns = 2 * time.Second

	// MinTimeToCorrectAfterTurn is the minimum time to correct after a turn
	MinTimeToCorrectAfterTurn = 1500 * time.Millisecond

	// UpdateDelay is the delay between updates
	UpdateDelay = 10 * time.Millisecond

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

	// FrontDistanceChange is the scalar change for the safety front distance calculation
	FrontDistanceChange = 1.25

	// SideDistanceChange is the scalar change for the side distance calculation
	SideDistanceChange = 1.1
)
