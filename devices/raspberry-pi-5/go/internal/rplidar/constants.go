package rplidar

import (
	"path/filepath"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// SlamtecC1BaudRate is the RPLiDAR C1 baud rate
	SlamtecC1BaudRate = 460800

	// SlamtecC1Port is the RPLiDAR C1 default port
	SlamtecC1Port = "/dev/ttyUSB0"

	// MaxDistanceLimit is the maximum distance limit
	MaxDistanceLimit = 3000

	// UltraSimpleName is the name of the Slamtec executable
	UltraSimpleName = "ultra_simple"

	// HandlerStartedMessage is the message logged when the handler starts
	HandlerStartedMessage = "RPLiDAR handler started"

	// CloseTimeout is the timeout for closing the handler
	CloseTimeout = 5 * time.Second

	// InitialSizeBuffer is the initial size of the buffer for reading lines
	InitialSizeBuffer = 1024 * 1024 // 1 MB

	// MaxSizeBuffer is the maximum size of the buffer for reading lines
	MaxSizeBuffer = 1024 * 1024 * 10 // 10 MB

	// StdoutTag is the tag for standard output logs
	StdoutTag = "STDOUT"

	// StderrTag is the tag for standard error logs
	StderrTag = "STDERR"

	// IgnoreFirstStdoutMessages is the number of initial stdout messages to ignore
	IgnoreFirstStdoutMessages = 6

	// UltraSimpleChannelArgument is the argument for the channel in the ultra_simple executable
	UltraSimpleChannelArgument = "--channel"

	// UltraSimpleSerialArgument is the argument for the serial port in the ultra_simple executable
	UltraSimpleSerialArgument = "--serial"

	// LoggerTag is the logger tag for RPLiDAR
	LoggerTag = "RPLiDAR"
)

var (
	// UltraSimplePath is the path where the Slamtec executable is stored
	UltraSimplePath string
)

func init() {
	// Initialize UltraSimplePath with the correct path
	UltraSimplePath = filepath.Join(internal.BinaryFolderPath, UltraSimpleName)
}
