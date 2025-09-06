package internal

import (
	"context"
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

// StopContextOnError stops the given context if an error is encountered.
//
// Parameters:
//
// ctx: The context to be stopped.
// stopFn: A function that stops the context with a given error.
// fn: A function that returns an error.
// loggerProducer: The logger producer to log messages.
//
// Returns:
//
// A function that executes the provided function and stops the context if an error occurs.
func StopContextOnError(
	ctx context.Context,
	stopFn func(),
	fn func(context.Context) error,
) func() error {
	return func() error {
		if err := fn(ctx); err != nil {
			if stopFn != nil {
				stopFn()
			}
			return err
		}
		return nil
	}
}
