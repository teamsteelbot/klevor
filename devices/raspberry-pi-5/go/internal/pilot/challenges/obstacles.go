package challenges

import (
	"context"
	"fmt"
	"math"
	"time"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
)

const (
	// CameraRangeThreshold is used to determine if an object is capable of being detected by the camera (only used in the closed challenge)
	CameraRangeThreshold = 250.0

	// MinDistanceOnFrontToAvoidObstacle is the minimum distance on front to avoid an obstacle
	MinDistanceOnFrontToAvoidObstacle = 150.0

	// MinDistanceOnOppositeSideToAvoidObstacle is the minimum distance on the opposite side to avoid an obstacle
	MinDistanceOnOppositeSideToAvoidObstacle = 225.0
)

// avoidObstacles is a function that makes the robot avoid obstacles using the RPLiDAR and CLIP classification
//
// Parameters:
//
// ctx: The context to use for the challenge
// service: The service to use for the challenge
// isObjectAvoidanceInProgress: A flag indicating if the robot is currently avoiding an obstacle
// loggerProducer: The logger producer to use for logging
//
// Returns:
//
// An error if the robot could not avoid obstacles, nil otherwise
func avoidObstacles(
	ctx context.Context,
	service Service,
	isObjectAvoidanceInProgress *bool,
	loggerProducer goconcurrentlogger.LoggerProducer,
) (internalclip.PositiveLabel, error) {
	// Check if the service is nil
	if service == nil {
		return internalclip.PositiveLabelNil, ErrNilService
	}

	// Check if the isObjectAvoidanceInProgress is nil
	if isObjectAvoidanceInProgress == nil {
		return internalclip.PositiveLabelNil, ErrNilIsObjectAvoidanceInProgress
	}

	// After each turn, the robot starts looking for the objects (it should be roughly centered, and it could gather the objects position, (left or right lane) with the rplidar)
	var obstacleDetected *gohailocliphandler.Classification
	var cardinalDirectionWithObstacle gorplidarsdkhandler.CardinalDirection
	for _, cardinalDirection := range ObstaclesDetectionCardinalDirections {
		// Get the average distance and average distance change for the cardinal direction
		distance := service.GetRPLiDARAverageDistance(cardinalDirection)
		distanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirection)

		// If the distance is NaN, continue to the next cardinal direction
		if math.IsNaN(distance) || math.IsNaN(distanceChange) {
			continue
		}

		// Check if the average distance and average distance change are below the threshold
		if distance+distanceChange <= CameraRangeThreshold {
			// Get the CLIP classification
			obstacleDetected = service.GetCLIPClassification()
			cardinalDirectionWithObstacle = cardinalDirection
			break
		}
	}

	// Check if there is an obstacle detected
	if obstacleDetected == nil {
		// If there was an obstacle avoidance in progress, log that the obstacle is no longer detected
		if *isObjectAvoidanceInProgress && loggerProducer != nil {
			loggerProducer.Info("Obstacle no longer detected")
		}

		// Set the isObjectAvoidanceInProgress to false
		*isObjectAvoidanceInProgress = false
		return internalclip.PositiveLabelNil, nil
	}

	// Log the obstacle detected only if there wasn't an obstacle avoidance in progress
	if !*isObjectAvoidanceInProgress && loggerProducer != nil {
		loggerProducer.Info(
			fmt.Sprintf(
				"Obstacle detected: %s at %s direction",
				obstacleDetected.GetLabel(),
				cardinalDirectionWithObstacle.String(),
			),
		)
	}

	// Get the corresponding positive label
	var positiveLabel internalclip.PositiveLabel
	switch obstacleDetected.GetLabel() {
	case internalclip.PositiveLabelRedBlock.String():
		positiveLabel = internalclip.PositiveLabelRedBlock
	case internalclip.PositiveLabelGreenBlock.String():
		positiveLabel = internalclip.PositiveLabelGreenBlock
	}

	// Stop the motor before avoiding the obstacle if it wasn't already avoiding an obstacle
	if !*isObjectAvoidanceInProgress {
		if err := service.SetMotorStop(ctx); err != nil {
			return positiveLabel, err
		}
	}

	// Set the isObjectAvoidanceInProgress flag to true
	*isObjectAvoidanceInProgress = true

	// Get the classification and is corresponding action
	var servoAngle float64
	var servoDirection ServoDirection
	var objectDetectionDirection ObjectDetectionDirection
	var objectDetectionIsOnOppositeSide bool
	var objectDetectionIsOnFront bool
	switch obstacleDetected.GetLabel() {
	case internalclip.PositiveLabelRedBlock.String():
		// Set the servo direction to right
		servoDirection = ServoDirectionRight

		// Check in which direction the obstacle is detected
		objectDetectionDirection = ObjectDetectionDirectionFromCardinalDirection(cardinalDirectionWithObstacle)
		switch objectDetectionDirection {
		case ObjectDetectionDirectionLeft:
			servoAngle = ServoObjectAvoidanceOnSameSideAngle
		case ObjectDetectionDirectionRight:
			servoAngle = ServoObjectAvoidanceOnOppositeSideAngle
			objectDetectionIsOnOppositeSide = true
		case ObjectDetectionDirectionFront:
			servoAngle = ServoObjectAvoidanceOnFrontAngle
			objectDetectionIsOnFront = true
		default:
			return positiveLabel, fmt.Errorf(
				"invalid object detection direction: %s",
				objectDetectionDirection.String(),
			)
		}
	case internalclip.PositiveLabelGreenBlock.String():
		// Set the servo direction to left
		servoDirection = ServoDirectionLeft

		// Check in which direction the obstacle is detected
		objectDetectionDirection = ObjectDetectionDirectionFromCardinalDirection(cardinalDirectionWithObstacle)
		switch objectDetectionDirection {
		case ObjectDetectionDirectionLeft:
			servoAngle = ServoObjectAvoidanceOnOppositeSideAngle
			objectDetectionIsOnOppositeSide = true
		case ObjectDetectionDirectionRight:
			servoAngle = ServoObjectAvoidanceOnSameSideAngle
		case ObjectDetectionDirectionFront:
			servoAngle = ServoObjectAvoidanceOnFrontAngle
			objectDetectionIsOnFront = true
		default:
			return positiveLabel, fmt.Errorf(
				"invalid object detection direction: %s",
				objectDetectionDirection.String(),
			)
		}
	}

	// Check if the object is too close and go backward until it's safe to avoid the obstacle
	objectTooClose := true
	goingBackward := false
	for objectTooClose && (objectDetectionIsOnOppositeSide || objectDetectionIsOnFront) {
		// Sleep for a short duration to avoid busy waiting
		time.Sleep(UpdateDelay)

		select {
		case <-ctx.Done():
			return positiveLabel, ctx.Err()
		default:
			// Check the backward distances to avoid a collision
			for _, cardinalDirection := range BackCardinalDirections {
				// Get the cardinal direction average distance and average distance change
				cardinalDirectionDistance := service.GetRPLiDARAverageDistance(cardinalDirection)
				cardinalDirectionDistanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirection)

				// If any measure is NaN, continue to the next cardinal direction
				if math.IsNaN(cardinalDirectionDistance) || math.IsNaN(cardinalDirectionDistanceChange) {
					continue
				}

				// Get the appropriate back distance threshold based on the cardinal direction
				backStopDistanceThreshold := getBackStopDistanceThresholdFromCardinalDirection(cardinalDirection)

				// Check if the object is still too close
				if cardinalDirectionDistance+cardinalDirectionDistanceChange < backStopDistanceThreshold {
					objectTooClose = false
					break
				}
			}

			// Get the cardinal direction average distance and average distance change
			cardinalDirectionDistance := service.GetRPLiDARAverageDistance(cardinalDirectionWithObstacle)
			cardinalDirectionDistanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirectionWithObstacle)

			// If any measure is NaN, continue
			if math.IsNaN(cardinalDirectionDistance) || math.IsNaN(cardinalDirectionDistanceChange) {
				continue
			}

			// Check if the object is still too close
			if objectDetectionIsOnOppositeSide && cardinalDirectionDistance+cardinalDirectionDistanceChange >= MinDistanceOnOppositeSideToAvoidObstacle {
				objectTooClose = false
				if loggerProducer != nil {
					loggerProducer.Info(
						fmt.Sprintf(
							"Object on opposite side is no longer too close: %s at %s direction",
							obstacleDetected.GetLabel(),
							cardinalDirectionWithObstacle.String(),
						),
					)
				}
				break
			} else if objectDetectionIsOnFront && cardinalDirectionDistance+cardinalDirectionDistanceChange >= MinDistanceOnFrontToAvoidObstacle {
				objectTooClose = false
				if loggerProducer != nil {
					loggerProducer.Info(
						fmt.Sprintf(
							"Object is no longer too close: %s at %s direction",
							obstacleDetected.GetLabel(),
							cardinalDirectionWithObstacle.String(),
						),
					)
				}
				break
			}

			// Set the motor to backward if not already set and the object is still too close
			if !goingBackward {
				// Set the servo to the given angle and direction to avoid the obstacle if it's not in front
				if objectDetectionDirection != ObjectDetectionDirectionFront {
					if err := service.SetServoAngle(
						ctx,
						servoAngle,
						servoDirection,
					); err != nil {
						return positiveLabel, err
					}
				}

				// Set the motor to backward
				if err := service.SetMotorBackward(
					ctx,
					MotorBackwardNormalSpeed,
				); err != nil {
					return positiveLabel, err
				}

				// Log the motor set to backward
				goingBackward = true
			}
		}
	}

	// Stop the motor before turning the servo
	if err := service.SetMotorStop(ctx); err != nil {
		return positiveLabel, err
	}

	// Set the servo angle and direction to avoid the obstacle
	if err := service.SetServoAngle(
		ctx,
		servoAngle,
		servoDirection,
	); err != nil {
		return positiveLabel, err
	}

	// Move forward to avoid the obstacle
	if err := service.SetMotorForward(
		ctx,
		MotorForwardNormalSpeed,
	); err != nil {
		return positiveLabel, err
	}
	return positiveLabel, nil
}
