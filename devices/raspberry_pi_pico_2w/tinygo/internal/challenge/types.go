package challenge

import "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pulldown"

type (
	// DefaultHandler is the default implementation of the Handler interface.
	DefaultHandler struct {
		obstaclesPullDownHandler pulldown.Handler
		parkingPullDownHandler   pulldown.Handler
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// pullDownHandler: The pull-down handler to use
//
// Returns:
//
// An instance of DefaultHandler, or an error if the pull-down handler is nil
func NewDefaultHandler(
	obstaclesPullDownHandler pulldown.Handler,
	parkingPullDownHandler pulldown.Handler,
) (*DefaultHandler, error) {
	if obstaclesPullDownHandler == nil {
		return nil, ErrNilObstaclesPullDownHandler
	}
	if parkingPullDownHandler == nil {
		return nil, ErrNilParkingPullDownHandler
	}

	return &DefaultHandler{
		obstaclesPullDownHandler,
		parkingPullDownHandler,
	}, nil
}

// IsWithObstacles checks if the challenge is with obstacles but not parking.
func (d *DefaultHandler) IsWithObstacles() bool {
	return d.obstaclesPullDownHandler.IsShorted() && d.parkingPullDownHandler.IsOpen()
}

// IsWithObstaclesAndParking checks if the challenge is with obstacles and parking.
func (d *DefaultHandler) IsWithObstaclesAndParking() bool {
	return d.obstaclesPullDownHandler.IsShorted() && d.parkingPullDownHandler.IsShorted()
}

// IsWithoutObstacles checks if the challenge is without obstacles.
func (d *DefaultHandler) IsWithoutObstacles() bool {
	return d.obstaclesPullDownHandler.IsOpen()
}
