package challenges

import (
	"time"

	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

const (
	// ServiceLoggerProducerTag is the tag for the service logger producer
	ServiceLoggerProducerTag = "CHALLENGE_SERVICE"

	// ChallengeHandlerLoggerProducerTag is the tag for the challenge handler logger producer
	ChallengeHandlerLoggerProducerTag = "CHALLENGE_HANDLER"

	// Algorithm90DegreeTurns is the number of 90 degree turns in the algorithm
	Algorithm90DegreeTurns = 12

	// MinTimeBetweenTurns is the minimum time between turns
	MinTimeBetweenTurns = 2 * time.Second

	// MinTimeToCorrectAfterTurn is the minimum time to correct after a turn
	MinTimeToCorrectAfterTurn = 1 * time.Second // 1500 * time.Millisecond

	// UpdateDelay is the delay between updates
	UpdateDelay = 10 * time.Millisecond

	// MaxDistanceChange is the maximum distance change for safety calculations
	MaxDistanceChange = 75.0

	// MotorBackwardFastSpeed of speed for fast backward motor speed
	MotorBackwardFastSpeed float64 = 1

	// MotorBackwardNormalSpeed of speed for normal backward motor speed
	MotorBackwardNormalSpeed float64 = 0.8

	// MotorBackwardSlowSpeed of speed for slow backward motor speed
	MotorBackwardSlowSpeed float64 = 0.6

	// MotorForwardFastSpeed of speed for fast forward motor speed
	MotorForwardFastSpeed float64 = 1

	// MotorForwardNormalSpeed of speed for normal forward motor speed
	MotorForwardNormalSpeed float64 = 0.8

	// MotorForwardSlowSpeed of speed for slow forward motor speed
	MotorForwardSlowSpeed float64 = 0.6

	// MotorTurningSpeed of speed for turning motor speed
	MotorTurningSpeed float64 = 0.8

	// ServoBigTurnAngle of angle for big turns
	ServoBigTurnAngle float64 = 1

	// ServoMediumTurnAngle of angle for medium turns
	ServoMediumTurnAngle float64 = 0.66

	// ServoSmallTurnAngle of angle for small turns
	ServoSmallTurnAngle float64 = 0.33

	// ServoObjectAvoidanceOnFrontAngle is the percentage of the angle for object avoidance on front
	ServoObjectAvoidanceOnFrontAngle float64 = 0.75

	// ServoObjectAvoidanceOnSameSideAngle of angle for object avoidance on same side
	ServoObjectAvoidanceOnSameSideAngle float64 = 0.25

	// ServoObjectAvoidanceOnOppositeSideAngle of angle for object avoidance on opposite side
	ServoObjectAvoidanceOnOppositeSideAngle float64 = 1

	// FrontDistanceChange is the scalar change for the safety front distance calculation
	FrontDistanceChange = 1.25

	// BackDistanceChange is the scalar change for the back distance calculation
	BackDistanceChange = 1.2

	// SideDistanceChange is the scalar change for the side distance calculation
	SideDistanceChange = 1.1

	// SafetyFrontDistanceStartThreshold is the distance threshold to start safety mode
	SafetyFrontDistanceStartThreshold = 150.0

	// SafetyFrontDistanceStopThreshold is the distance threshold to stop safety mode
	SafetyFrontDistanceStopThreshold = 350.0

	// SafetyBackDistanceThreshold is the distance threshold to stop moving backward
	SafetyBackDistanceThreshold = 125.0
)

var (
	// FrontDistanceTurningCardinalDirections are the cardinal directions to check for safety front distance when turning
	FrontDistanceTurningCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNortheast,
	}

	// FrontDistanceStraightCardinalDirections are the cardinal directions to check for safety front distance when going straight
	FrontDistanceStraightCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
	}

	// ObjectDetectionFrontCardinalDirections are the cardinal directions for object detection front distance
	ObjectDetectionFrontCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
	}

	// ObjectDetectionLeftCardinalDirections are the cardinal directions for object detection left distance
	ObjectDetectionLeftCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionWest,
		gorplidarsdkhandler.CardinalDirectionWestNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorthwest,
	}

	// ObjectDetectionRightCardinalDirections are the cardinal directions for object detection right distance
	ObjectDetectionRightCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionEast,
		gorplidarsdkhandler.CardinalDirectionEastNortheast,
		gorplidarsdkhandler.CardinalDirectionNortheast,
	}

	// ObstaclesDetectionCardinalDirections are the cardinal directions to check for obstacles detection
	ObstaclesDetectionCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionWest,
		gorplidarsdkhandler.CardinalDirectionWestNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest,
		gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNortheast,
		gorplidarsdkhandler.CardinalDirectionEastNortheast,
		gorplidarsdkhandler.CardinalDirectionEast,
	}

	// BackCardinalDirections are the cardinal directions to check for safety back distance
	BackCardinalDirections = []gorplidarsdkhandler.CardinalDirection{
		gorplidarsdkhandler.CardinalDirectionSouthSoutheast,
		gorplidarsdkhandler.CardinalDirectionSouthSouthwest,
	}
)
