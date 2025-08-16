package challenge

import (
	"errors"
)

var (
	ErrNilHandler                  = errors.New("challenge handler cannot be nil")
	ErrNilObstaclesPullDownHandler = errors.New("obstacles pull-down handler cannot be nil")
	ErrNilParkingPullDownHandler   = errors.New("parking pull-down handler cannot be nil")
)
