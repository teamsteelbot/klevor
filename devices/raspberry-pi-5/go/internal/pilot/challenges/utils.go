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


// getFrontDistanceChangeBasedOnTheCardinalDirections returns the front distance change based on the cardinal directions
//
// Parameters:
//
// cardinalDirections: A slice of cardinal directions to check the front distances.
//
// Returns:
//
// A float64 representing the front distance change based on the cardinal directions
func getFrontDistanceChangeBasedOnTheCardinalDirections(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64 {
	switch cardinalDirection {
	case gorplidarsdkhandler.CardinalDirectionNorth,
		gorplidarsdkhandler.CardinalDirectionNorthNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthNorthwest:
		return FrontDistanceChange
	case gorplidarsdkhandler.CardinalDirectionNortheast,
		gorplidarsdkhandler.CardinalDirectionNorthwest:
		return FrontDiagonalDistanceChange
	default:
		return 1.0
	}
}

// getBackDistanceChangeBasedOnTheCardinalDirections returns the back distance change based on the cardinal directions
//
// Parameters:
//
// cardinalDirection: The cardinal direction to check the back distances.
//
// Returns:
//
// A float64 representing the back distance change based on the cardinal directions
func getBackDistanceChangeBasedOnTheCardinalDirections(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64 {
	switch cardinalDirection {
	case gorplidarsdkhandler.CardinalDirectionSouthSoutheast,
		gorplidarsdkhandler.CardinalDirectionSouthSouthwest:
		return BackDistanceChange
	case gorplidarsdkhandler.CardinalDirectionSoutheast,
		gorplidarsdkhandler.CardinalDirectionSouthwest:
		return BackDiagonalDistanceChange
	default:
		return 1.0
	}
}