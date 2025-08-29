package rplidar

import (
	"context"
)

type (
	// Handler is the interface to handle the RPLIDAR device
	Handler interface {
		ReadIncomingMeasures(ctx context.Context) error
	}
)
