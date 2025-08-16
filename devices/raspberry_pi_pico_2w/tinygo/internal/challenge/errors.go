package challenge

import (
	"errors"
)

var (
	ErrNilObstaclesPullDownHandler = errors.New("obstacles pull-down handler cannot be nil")
	ErrNilParkingPullDownHandler   = errors.New("parking pull-down handler cannot be nil")
)
