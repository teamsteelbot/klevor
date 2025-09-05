package pilot

import (
	"context"
)

type (
	// Handler is the interface for the pilot handler
	Handler interface {
		Run() error
		IsRunning() bool
		challengeWithObstaclesHandler(ctx context.Context) error
		challengeWithoutObstaclesHandler(ctx context.Context) error
	}
)
