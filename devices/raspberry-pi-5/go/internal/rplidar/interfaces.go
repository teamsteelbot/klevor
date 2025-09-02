package rplidar

import (
	"context"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Handler is the interface to handle the RPLIDAR device
	Handler interface {
		ReadIncomingMeasures(ctx context.Context) error
		GetMeasures() *[360]*internal.Measure
	}
)
