package rplidar

import (
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
)

// NewSlamtecC1Handler is the constructor for the Slamtec C1 handler
//
// Parameters:
//
// logger: The logger instance to use
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the Slamtec C1 handler and an error if any
func NewSlamtecC1Handler(
	logger goconcurrentlogger.Logger,
	debug bool,
) (*gorplidarsdkhandler.DefaultHandler, error) {
	return gorplidarsdkhandler.NewSlamtecC1Handler(
		gorplidarsdkhandler.LinuxSlamtecC1Port,
		IsUpsideDown,
		AngleAdjustment,
		MinimumQuality,
		logger,
		UltraSimplePath,
		MaxDistanceLimit,
		MeasuresChSize,
		debug,
	)
}
