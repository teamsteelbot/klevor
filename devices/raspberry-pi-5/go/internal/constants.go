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
