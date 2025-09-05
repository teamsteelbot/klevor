package rplidar

import (
	"context"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Handler is the interface to handle the RPLiDAR device
	Handler interface {
		Run(ctx context.Context, stopFn func()) error
		IsRunning() bool
		GetMeasures() *[360]*internal.Measure
		GetRotationCompletedChannel() <-chan RotationCompleted
	}
)
