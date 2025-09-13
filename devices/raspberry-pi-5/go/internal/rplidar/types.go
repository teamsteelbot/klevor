package rplidar

import (
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
)

// NewSlamtecC1Handler is the constructor for the Slamtec C1 handler
//
// Parameters:
//
// logger: The logger instance to use
//
// Returns:
//
// A pointer to the Slamtec C1 handler and an error if any
func NewSlamtecC1Handler(logger goconcurrentlogger.Logger) (*gorplidarsdkhandler.DefaultHandler, error) {
	return gorplidarsdkhandler.NewSlamtecC1Handler(
		gorplidarsdkhandler.LinuxSlamtecC1Port,
		IsUpsideDown,
		AngleAdjustment,
		logger,
		UltraSimplePath,
		ChannelBufferSize,
		MaxDistanceLimit,
	)
}