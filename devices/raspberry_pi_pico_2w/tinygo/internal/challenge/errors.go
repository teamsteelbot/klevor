package challenge

import (
	"errors"
)

var (
	ErrNilHandler                = errors.New("challenge handler cannot be nil")
	ErrNilObstaclesPullUpHandler = errors.New("obstacles pull-up handler cannot be nil")
	ErrNilParkingPullUpHandler   = errors.New("parking pull-up handler cannot be nil")
)
