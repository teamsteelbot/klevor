package rplidar

import (
	"path/filepath"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// C1BaudRate is the RPLiDAR C1 baud rate
	C1BaudRate = 460800

	// C1Port is the RPLiDAR C1 default port
	C1Port = "/dev/ttyUSB0"

	// MaxDistanceLimit is the maximum distance limit
	MaxDistanceLimit = 3000

	// DistanceDiff is the distance difference
	DistanceDiff = 25

	// UltraSimpleName is the name of the Slamtec executable
	UltraSimpleName = "ultra_simple"
)

var (
	// UltraSimplePath is the path where the Slamtec executable is stored
	UltraSimplePath string
)

func init() {
	// Initialize UltraSimplePath with the correct path
	UltraSimplePath = filepath.Join(internal.BinaryFolderPath, UltraSimpleName)
}
