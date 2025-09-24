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
