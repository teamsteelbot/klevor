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
//
// Returns:
//
// The error returned by the function, if any.
func StopContextOnError(
	ctx context.Context,
	stopFn func(),
	fn func(ctx2 context.Context) error,
) error {
	if err := fn(ctx); err != nil {
		stopFn()
		return err
	}
	return nil
}
