package challenges

import (
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

// getFrontDistanceCardinalDirections returns the list of cardinal directions
//
// Parameters:
//
// isTurning: A flag indicating if the robot is currently turning.
//
// Returns:
//
// A slice of cardinal directions to check the front distances (e.g., North, North-Northeast, North-Northwest)
func getFrontDistanceCardinalDirections(isTurning bool) []gorplidarsdkhandler.CardinalDirection {
	if isTurning {
		return FrontDistanceTurningCardinalDirections
	}
	return FrontDistanceStraightCardinalDirections
}

// getFrontStartDistanceThresholdFromCardinalDirection returns the front start distance threshold based on the cardinal direction
//
// Parameters:
//
// cardinalDirection: The cardinal direction to check the front distance start threshold.
//
// Returns:
//
// A float64 representing the front start distance threshold based on the cardinal direction
func getFrontStartDistanceThresholdFromCardinalDirection(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64 {
	switch cardinalDirection {
	case gorplidarsdkhandler.CardinalDirectionNorth:
		return FrontStartDistanceThreshold
	case gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest:
		return FrontSemiDiagonalStartDistanceThreshold
	case gorplidarsdkhandler.CardinalDirectionNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthwest:
		return FrontDiagonalStartDistanceThreshold
	default:
		return FrontStartDistanceThreshold
	}
}

// getFrontStopDistanceThresholdFromCardinalDirection returns the front stop distance threshold based on the cardinal direction
//
// Parameters:
//
// cardinalDirection: The cardinal direction to check the front distance stop threshold.
//
// Returns:
//
// A float64 representing the front stop distance threshold based on the cardinal direction
func getFrontStopDistanceThresholdFromCardinalDirection(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64 {
	switch cardinalDirection {
	case gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest:
		return FrontStopDistanceThreshold
	case gorplidarsdkhandler.CardinalDirectionNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthwest:
		return FrontDiagonalStopDistanceThreshold
	default:
		return FrontStopDistanceThreshold
	}
}

// getBackStopDistanceThresholdFromCardinalDirection returns the back stop distance threshold based on the cardinal direction
//
// Parameters:
//
// cardinalDirection: The cardinal direction to check the back stop distances threshold.
//
// Returns:
//
// A float64 representing the back stop distance threshold based on the cardinal direction
func getBackStopDistanceThresholdFromCardinalDirection(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64 {
	switch cardinalDirection {
	case gorplidarsdkhandler.CardinalDirectionSouthSoutheast,
		gorplidarsdkhandler.CardinalDirectionSouthSouthwest:
		return BackStopDistanceThreshold
	case gorplidarsdkhandler.CardinalDirectionSoutheast,
		gorplidarsdkhandler.CardinalDirectionSouthwest:
		return BackDiagonalStopDistanceThreshold
	default:
		return BackStopDistanceThreshold
	}
}
