package challenges

import (
	"context"
	"fmt"
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
// isTurning: A flag indicating if the robot is currently turning
// isObjectAvoidanceInProgress: A flag indicating if the robot is currently avoiding an obstacle
// loggerProducer: The logger producer to use for logging
//
// Returns:
//
// A boolean indicating if an obstacle was avoided, and an error if the obstacle could not be avoided, nil otherwise
func avoidObstacles(
	ctx context.Context,
	service Service,
	isTurning bool,
	isObjectAvoidanceInProgress *bool,
	loggerProducer goconcurrentlogger.LoggerProducer,
) (bool, error) {
	// Check if the service is nil
	if service == nil {
		return false, ErrNilService
	}

	// Check if the robot is currently turning
	if isTurning {
		// If the robot is turning, do not attempt to avoid obstacles
		return false, nil
	}

	// Check if the isObjectAvoidanceInProgress is nil
	if isObjectAvoidanceInProgress == nil {
		return false, ErrNilIsObjectAvoidanceInProgress
	}

	// After each turn, the robot starts looking for the objects (it should be roughly centered, and it could gather the objects position, (left or right lane) with the rplidar)
	var obstacleDetected *gohailocliphandler.Classification
	var cardinalDirectionWithObstacle gorplidarsdkhandler.CardinalDirection
	for _, cardinalDirection := range ObstaclesDetectionCardinalDirections {
		// Get the average distance and average distance change for the cardinal direction
		averageDistance := service.GetRPLiDARAverageDistance(cardinalDirection)
		averageDistanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirection)

		// Check if the average distance and average distance change are below the threshold
		if averageDistance+averageDistanceChange <= CameraRangeThreshold {
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
		return false, nil
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

	// Stop the motor before avoiding the obstacle if it wasn't already avoiding an obstacle
	if !*isObjectAvoidanceInProgress {
		if err := service.SetMotorStop(ctx); err != nil {
			return true, err
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
			return false, fmt.Errorf(
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
			return false, fmt.Errorf(
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
			return false, ctx.Err()
		default:
			// Check the backward distances to avoid a collision
			for _, cardinalDirection := range BackCardinalDirections {
				// Get the cardinal direction average distance and average distance change
				cardinalDirectionDistance := service.GetRPLiDARAverageDistance(cardinalDirection)
				cardinalDirectionDistanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirection)

				// Check if the object is still too close
				if cardinalDirectionDistance+cardinalDirectionDistanceChange < SafetyBackDistanceThreshold {
					objectTooClose = false
					break
				}
			}

			// Get the cardinal direction average distance and average distance change
			cardinalDirectionDistance := service.GetRPLiDARAverageDistance(cardinalDirectionWithObstacle)
			cardinalDirectionDistanceChange := service.GetRPLiDARAverageDistanceChange(cardinalDirectionWithObstacle)

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
						return true, err
					}
				}

				// Set the motor to backward
				if err := service.SetMotorBackward(
					ctx,
					MotorBackwardNormalSpeed,
				); err != nil {
					return false, fmt.Errorf(
						"failed to set motor to backward speed: %w",
						err,
					)
				}

				// Log the motor set to backward
				goingBackward = true
			}
		}
	}

	// Stop the motor before turning the servo
	if err := service.SetMotorStop(ctx); err != nil {
		return true, err
	}

		// Set the servo angle and direction to avoid the obstacle
		if err := service.SetServoAngle(
			ctx,
			servoAngle,
			servoDirection,
		); err != nil {
			return true, err
		}

		/*
			if err := h.setMotorForwardByPercentage(
					ctx,
					MotorForwardNormalPercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set motor to normal speed: %w",
						err,
					)
				}
				if westAverageDistance <= float64(CameraRangeThreshold) && eastAverageDistance <= float64(CameraRangeThreshold) {
					if err := h.setServoToRightByPercentage(
						ctx,
						ServoMediumTurnAnglePercentage,
					); err != nil {
						return fmt.Errorf(
							"failed to set servo to small right turn: %w",
							err,
						)
					}
				}
				else if northAverageDistance <= float64(FrontCloseupThreshold) {
					if err := h.setServoToCenter(ctx); err != nil {
						return fmt.Errorf(
							"failed to set servo to center: %w",
							err,
						)
					}
					if err := h.setMotorBackwardByPercentage(
						ctx,
						MotorBackwardNormalPercentage,
					); err != nil {
						return fmt.Errorf(
							"failed to set motor to normal speed: %w",
							err,
						)
					}
					return
				}
		*/

		/*
			if err := h.setMotorForwardByPercentage(
				ctx,
				MotorForwardNormalPercentage,
			); err != nil {
				return fmt.Errorf(
					"failed to set motor to normal speed: %w",
					err,
				)
			}
			if westAverageDistance <= float64(CameraRangeThreshold) and eastAverageDistance <= float64(CameraRangeThreshold) {
				while (robot not aligned)
				if err := h.setServoToRightByPercentage(
					ctx,
					ServoMediumTurnAnglePercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set servo to small right turn: %w",
						err,
					)
				}
			}
			else if northAverageDistance <= float64(FrontCloseupThreshold) {
				if err := h.setServoToCenter(ctx); err != nil {
					return fmt.Errorf(
						"failed to set servo to center: %w",
						err,
					)
				}
				if err := h.setMotorBackwardByPercentage(
					ctx,
					MotorBackwardNormalPercentage,
				); err != nil {
					return fmt.Errorf(
						"failed to set motor to normal speed: %w",
						err,
					)
				}
				continue
			}
		*/
	}
	return true, nil
}
