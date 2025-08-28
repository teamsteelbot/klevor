package internal

import (
	"os"
	"path/filepath"
)

// ExecutableDir returns the directory where the running binary resides.
//
// Returns:
//
// The directory path as a string and an error if any occurs.
func ExecutableDir() (string, error) {
	exePath, err := os.Executable()
	if err != nil {
		return "", err
	}

	// Resolve symlinks (important if the binary is invoked via a symlink).
	resolved, err := filepath.EvalSymlinks(exePath)
	if err != nil {
		return "", err
	}
	return filepath.Dir(resolved), nil
}
