package internal

import (
	"path/filepath"
)

const (
	// BinaryFolderName is the name folder where the required binaries are located
	BinaryFolderName = "bin"

	// DataFolderName is the name of the folder where data files are stored
	DataFolderName = "data"

	// AttributesSeparator is the attributes separator
	AttributesSeparator = ","

	// SyncBitCharacter is the sync bit character
	SyncBitCharacter = "S"

	// AngleIndex is the index of the angle in the measure string
	AngleIndex = 0

	// DistanceIndex is the index of the distance in the measure string
	DistanceIndex = 1

	// QualityIndex is the index of the quality in the measure string
	QualityIndex = 2

	// LabelIndex is the index of the label in the classification string
	LabelIndex = 0

	// ConfidenceIndex is the index of the confidence in the classification string
	ConfidenceIndex = 1
)

var (
	// RootFolderPath is the path of the folder where the running binary resides
	RootFolderPath string

	// BinaryFolderPath is the path of the folder where the required binaries are located
	BinaryFolderPath string

	// DataFolderPath is the path of the folder where data files are stored
	DataFolderPath string
)

func init() {
	// Initialize RootFolderPath with the correct path
	dir, err := ExecutableDir()
	if err != nil {
		panic(err)
	}
	RootFolderPath = dir

	// Initialize BinaryFolderPath with the correct path
	BinaryFolderPath = filepath.Join(RootFolderPath, BinaryFolderName)

	// Initialize DataFolderPath with the correct path
	DataFolderPath = filepath.Join(RootFolderPath, DataFolderName)
}
