package rplidar

import (
	"path/filepath"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// SlamtecC1BaudRate is the RPLiDAR C1 baud rate
	SlamtecC1BaudRate = 460800

	// MaxDistanceLimit is the maximum distance limit
	MaxDistanceLimit = 3000

	// HandlerStartedMessage is the message logged when the handler starts
	HandlerStartedMessage = "RPLiDAR handler started"

	// CloseTimeout is the timeout for closing the handler
	CloseTimeout = 5 * time.Second

	// UltraSimpleChannelArgument is the argument for the channel in the ultra_simple executable
	UltraSimpleChannelArgument = "--channel"

	// UltraSimpleSerialArgument is the argument for the serial port in the ultra_simple executable
	UltraSimpleSerialArgument = "--serial"
)

var (
	// SlamtecC1Port is the RPLiDAR C1 default port
	SlamtecC1Port = "/dev/ttyUSB0"

	// UltraSimpleName is the name of the Slamtec executable
	UltraSimpleName = "ultra_simple"

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

	// ChannelBufferSize is the size of the rotation completed channel buffer
	ChannelBufferSize = 10

	// HandlerLoggerProducerTag is the logger producer tag for RPLiDAR
	HandlerLoggerProducerTag = "RPLiDAR_HANDLER"
)

var (
	// UltraSimplePath is the path where the Slamtec executable is stored
	UltraSimplePath string
)

func init() {
	// Initialize UltraSimplePath with the correct path
	UltraSimplePath = filepath.Join(internal.BinaryFolderPath, UltraSimpleName)
}
