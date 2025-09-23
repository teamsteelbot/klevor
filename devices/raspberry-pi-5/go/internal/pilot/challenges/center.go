package challenges

import (
	"context"
	"math"
	"time"

	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

const (
	// SideDistanceMediumDifferencePercentage is the percentage of medium difference threshold for side distances
	SideDistanceMediumDifferencePercentage = 0.35

	// SideDistanceSmallDifferencePercentage is the percentage of small difference threshold for side distances
	SideDistanceSmallDifferencePercentage = 0.15 // 0.2, 0.15, 0.3

	// GyroscopeTolerance is the tolerance for the gyroscope
	GyroscopeTolerance = 2.0

	// YawDegreesServoAngleRatio is the ratio between yaw degrees and servo angle
	YawDegreesServoAngleRatio = 2.0
)

// centerByRPLiDARHandler centers the robot using RPLiDAR data
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// lastTurningTime: The last time the robot made a turn
// turningDirection: The direction the robot turned (left or right)
//
// Returns:
//
// An error if the robot could not be centered, nil otherwise
func centerByRPLiDARHandler(
	ctx context.Context,
	service Service,
	lastTurningTime time.Time,
	turningDirection ServoDirection,
) error {
	// Get the rate of change for west and east average distances
	westAverageDistance := service.GetWestAverageDistance()
	eastAverageDistance := service.GetEastAverageDistance()
	westAverageDistanceChange := SideDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionWest)
	eastAverageDistanceChange := SideDistanceChange * service.GetRPLiDARAverageDistanceChange(gorplidarsdkhandler.CardinalDirectionEast)

	// Check if the servo should make a little turn to the left or right in order to center the robot
	if math.IsNaN(eastAverageDistance) || math.IsNaN(westAverageDistance) || time.Since(lastTurningTime) < MinTimeToCorrectAfterTurn {
		if err := service.SetServoToCenter(ctx); err != nil {
			return err
		}
	} else if eastAverageDistance+eastAverageDistanceChange >= (westAverageDistance+westAverageDistanceChange)*(1+SideDistanceMediumDifferencePercentage) {
		if err := service.SetServoToRight(
			ctx,
			ServoMediumCorrectionAnglePercentage,
		); err != nil {
			return err
		}
	} else if eastAverageDistance+eastAverageDistanceChange >= (westAverageDistance+westAverageDistanceChange)*(1+SideDistanceSmallDifferencePercentage) {
		if err := service.SetServoToRight(
			ctx,
			ServoSmallCorrectionAnglePercentage,
		); err != nil {
			return err
		}
	} else if westAverageDistance+westAverageDistanceChange >= (eastAverageDistance+eastAverageDistanceChange)*(1+SideDistanceMediumDifferencePercentage) {
		if err := service.SetServoToLeft(
			ctx,
			ServoMediumCorrectionAnglePercentage,
		); err != nil {
			return err
		}
	} else if westAverageDistance+westAverageDistanceChange >= (eastAverageDistance+eastAverageDistanceChange)*(1+SideDistanceSmallDifferencePercentage) {
		if err := service.SetServoToLeft(
			ctx,
			ServoSmallCorrectionAnglePercentage,
		); err != nil {
			return err
		}
	} else if err := service.SetServoToCenter(ctx); err != nil {
		return err
	}
	return nil
}

// centerByGyroscopeHandler centers the robot using gyroscope data
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// last90DegreeTurns: The last recorded number of 90-degree turns
//
// Returns:
//
// An error if the robot could not be centered, nil otherwise
func centerByGyroscopeHandler(
	ctx context.Context,
	service Service,
	last90DegreeTurns uint,
) error {
	// Get the latest accumulated yaw degrees value
	accumulatedYawDegrees := service.GetAccumulatedYawDegrees()

	// Get the difference of the accumulated yaw degrees from the last 90-degree turn
	var deltaYawDegrees float64
	if last90DegreeTurns == 0 {
		deltaYawDegrees = accumulatedYawDegrees
	} else if accumulatedYawDegrees >= 0 {
		deltaYawDegrees = accumulatedYawDegrees - float64(last90DegreeTurns)*90.0
	} else {
		deltaYawDegrees = accumulatedYawDegrees + float64(last90DegreeTurns)*90.0
	}

	// Check if the delta yaw degrees is within gyroscope tolerance
	if math.Abs(deltaYawDegrees) <= GyroscopeTolerance {
		if err := service.SetServoToCenter(ctx); err != nil {
			return err
		}
		return nil
	}

	// Check to which side the robot should turn to center itself
	gyroOrientation := service.GetGyroscopeOrientation()
	if gyroOrientation.IsToRight(deltaYawDegrees) {
		if err := service.SetServoToLeft(
			ctx,
			math.Min(1, YawDegreesServoAngleRatio*math.Abs(deltaYawDegrees)),
		); err != nil {
			return err
		}
	} else if gyroOrientation.IsToLeft(deltaYawDegrees) {
		if err := service.SetServoToRight(
			ctx,
			math.Min(1, YawDegreesServoAngleRatio*math.Abs(deltaYawDegrees)),
		); err != nil {
			return err
		}
	}
	return nil
}
