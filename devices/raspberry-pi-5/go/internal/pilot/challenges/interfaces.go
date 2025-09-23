package challenges

import (
	"context"

	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Service is the interface that defines the methods to interact with the challenges
	Service interface {
		Run(
			ctx context.Context,
			cancelFn context.CancelFunc,
			challenge internal.Challenge,
		) error
		IsRunning() bool
		WaitUntilReady(ctx context.Context) error
		GetGyroscopeOrientation() internal.GyroscopeOrientation
		GetMotorSpeed() float64
		GetMotorDirection() MotorDirection
		GetServoAngle() float64
		GetServoDirection() ServoDirection
		SetMotorSpeed(
			ctx context.Context,
			speed float64,
			direction MotorDirection,
		) error
		SetMotorStop(ctx context.Context) error
		SetMotorForward(ctx context.Context, speed float64) error
		SetMotorBackward(ctx context.Context, speed float64) error
		SetServoAngle(
			ctx context.Context,
			angle float64,
			direction ServoDirection,
		) error
		SetServoToCenter(ctx context.Context) error
		SetServoToLeft(ctx context.Context, anglePercentage float64) error
		SetServoToRight(ctx context.Context, anglePercentage float64) error
		SetServoToOppositeDirection(
			ctx context.Context,
			anglePercentage float64,
		) error
		GetSouthSouthwestAverageDistance() float64
		GetSouthSoutheastAverageDistance() float64
		GetWestAverageDistance() float64
		GetEastAverageDistance() float64
		GetNorthwestAverageDistance() float64
		GetNortheastAverageDistance() float64
		GetNorthAverageDistance() float64
		GetRPLiDARAverageDistance(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64
		GetRPLiDARAverageDistanceChange(cardinalDirection gorplidarsdkhandler.CardinalDirection) float64
		Get360DegreeTurns() uint
		Get90DegreeTurns() uint
		Get45DegreeTurns() uint
		Get30DegreeTurns() uint
		GetAccumulatedYawDegrees() float64
		GetCLIPClassification() *gohailocliphandler.Classification
	}
)
