package pilot

import (
	"time"
)

/*
# Start delay
START_DELAY = 5

# RPLidar wait delay
RPLIDAR_WAIT_DELAY = 0.1

# Update delay
MOTOR_DELAY = 0.2
SERVO_DELAY = 0.05
GYROSCOPE_DELAY = 0.05

# Wait timeout for the start event
START_WAIT_TIMEOUT = 0.1
*/

var (
	// IncomingDelay is the delay between incoming message checks
	IncomingDelay = 10 * time.Millisecond

	// ConfirmationTimeout is the timeout duration for confirmation messages
	ConfirmationTimeout = 5 * time.Second

	// ConfirmationMessageTimeout is the timeout duration for confirmation messages
	ConfirmationMessageTimeout = time.Second * 5

	// StopTimeout is the timeout duration for stopping the USB-CDC communication
	StopTimeout = 5 * time.Second

	// ConfirmationAttempts is the number of attempts to confirm a message
	ConfirmationAttempts = ConfirmationTimeout / IncomingDelay

	// LoggerProducerTag is the tag for the logger producer
	LoggerProducerTag = "PILOT"

	// MotorFastPercentage is the percentage of the maximum speed for fast motor speed
	MotorFastPercentage = 0.7

	// MotorNormalPercentage is the percentage of the maximum speed for normal motor speed
	MotorNormalPercentage = 0.5

	// MotorSlowPercentage is the percentage of the maximum speed for slow motor speed
	MotorSlowPercentage = 0.3

	// ServoBigTurnAnglePercentage is the percentage of the maximum angle for big turns
	ServoBigTurnAnglePercentage = 1

	// ServoMediumTurnAnglePercentage is the percentage of the maximum angle for medium turns
	ServoMediumTurnAnglePercentage = 0.75

	// ServoSmallTurnAnglePercentage is the percentage of the maximum angle for small turns
	ServoSmallTurnAnglePercentage = 0.5

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
