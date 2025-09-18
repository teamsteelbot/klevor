package rplidar

import (
	"path/filepath"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// IsUpsideDown indicates if the RPLidar is mounted upside down
	IsUpsideDown = true

	// AngleAdjustment is the angle adjustment in degrees
	AngleAdjustment = 0

	// MaxDistanceLimit is the maximum distance limit
	MaxDistanceLimit = 3000

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
