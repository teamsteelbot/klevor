package challenges

import (
	"time"

	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

// MOTOR: MIN SPEED = 0.65 (0.55 didn't work well)

const (
	// ServiceLoggerProducerTag is the tag for the service logger producer
	ServiceLoggerProducerTag = "CHALLENGE_SERVICE"

	// ChallengeHandlerLoggerProducerTag is the tag for the challenge handler logger producer
	ChallengeHandlerLoggerProducerTag = "CHALLENGE_HANDLER"

	// Algorithm90DegreeTurns is the number of 90 degree turns in the algorithm
	Algorithm90DegreeTurns = 12

	// UpdateDelay is the delay between updates
	UpdateDelay = 10 * time.Millisecond

	// MaxDistanceChange is the maximum distance change for safety calculations
	MaxDistanceChange = 350.0 // 75.0, 200.0, 250.0, 350.0

	// MotorBackwardFastSpeed of speed for fast backward motor speed
	MotorBackwardFastSpeed float64 = 0.6 // 1 (not too charged), 0.9, 0.75 (full charged)

	// MotorBackwardNormalSpeed of speed for normal backward motor speed
	MotorBackwardNormalSpeed float64 = 0.5 // 0.8 (not too charged), 0.7, 0.675, 0.6, 0.5, 0.4 (full charged)

	// MotorBackwardSlowSpeed of speed for slow backward motor speed
	MotorBackwardSlowSpeed float64 = 0.4 // 0.6 (not too charged), 0.55, 0.6 (full charged)

	// MotorForwardFastSpeed of speed for fast forward motor speed
	MotorForwardFastSpeed float64 = 0.6 // 1 (not too charged), 0.9, 0.875, 0.75, 0.675, 0.6 (full charged)

	// MotorForwardNormalSpeed of speed for normal forward motor speed
	MotorForwardNormalSpeed float64 = 0.5 // 0.8 (not too charged), 0.7, 0.675, 0.6, 0.5 (full charged)

	// MotorForwardSlowSpeed of speed for slow forward motor speed
	MotorForwardSlowSpeed float64 = 0.4 // 0.6 (not too charged), 0.55, 0.6, 0.5, 0.4 (full charged)

	// MotorTurningSpeed of speed for turning motor speed
	MotorTurningSpeed float64 = 0.5 // 0.75 (not too charged), 0.65, 0.5 (full charged)

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
	FrontDistanceChange = 3.0 // 1.5, 2.0, 2.5, 3.0

	// FrontDiagonalDistanceChange is the scalar change for the front diagonal distance calculation
	FrontDiagonalDistanceChange = 2.5 // 1.5, 2.0, 2.5

	// BackDistanceChange is the scalar change for the back distance calculation
	BackDistanceChange = 2 // 1.0, 1.5, 2.0

	// BackDiagonalDistanceChange is the scalar change for the back diagonal distance calculation
	BackDiagonalDistanceChange = 2.0

	// FrontStartDistanceThreshold is the distance threshold to start the collision handler when an obstacle is detected in the front directions
	FrontStartDistanceThreshold = 160.0

	// FrontSemiDiagonalStartDistanceThreshold is the distance threshold to start the collision handler when an obstacle is detected in the front semi-diagonal directions
	FrontSemiDiagonalStartDistanceThreshold = 200.0

	// FrontDiagonalStartDistanceThreshold is the distance threshold to start the collision handler when an obstacle is detected in the front diagonal directions
	FrontDiagonalStartDistanceThreshold = 240.0

	// FrontStopDistanceThreshold is the distance threshold to stop the collision handler when an obstacle is detected in the front directions
	FrontStopDistanceThreshold = 400.0

	// FrontDiagonalStopDistanceThreshold is the distance threshold to stop the collision handler when an obstacle is detected in the front diagonal directions
	FrontDiagonalStopDistanceThreshold = 420.0

	// BackStopDistanceThreshold is the distance threshold to stop the collision handler when an obstacle is detected in the back directions
	BackStopDistanceThreshold = 350.0 // 350.0

	// BackDiagonalStopDistanceThreshold is the distance threshold to stop the collision handler when an obstacle is detected in the back diagonal directions
	BackDiagonalStopDistanceThreshold = 350.0 // 400.0, 325.0
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
		gorplidarsdkhandler.CardinalDirectionSouthwest,
		gorplidarsdkhandler.CardinalDirectionSouthSouthwest,
		gorplidarsdkhandler.CardinalDirectionSouthSoutheast,
		gorplidarsdkhandler.CardinalDirectionSoutheast,
	}
)
