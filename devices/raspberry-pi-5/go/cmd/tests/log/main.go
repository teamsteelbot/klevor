package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
)

const (
	// SimulateShutdownAfter for demonstration purposes, simulate shutdown after this duration
	SimulateShutdownAfter = 5 * time.Second

	// SendMessageInterval is the interval between sending messages
	SendMessageInterval = 10 * time.Millisecond

	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// TotalMessages to send before stopping
	TotalMessages = 100
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Initialize the logger
	logger := internallog.NewDefaultLogger(*logDebug)

	// Create a new logger producer
	loggerProducer, err := logger.NewProducer("TEST_PRODUCER")
	if err != nil {
		_, _ = fmt.Fprintf(
			os.Stderr,
			"failed to create logger producer: %v\n",
			err,
		)
		return
	}

	// Context canceled on SIGINT/SIGTERM.
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)
	defer stop()

	// Simulate shutdown on SIGINT
	go func() {
		time.Sleep(SimulateShutdownAfter)
		stop()
	}()

	// Example usage of the logger producer in a separate goroutine
	go func() {
		defer logger.Close()
		defer loggerProducer.Close()

		// Send messages
		for i := 0; i < TotalMessages; i++ {
			select {
			case <-ctx.Done():
				return
			default:
				loggerProducer.Info(fmt.Sprintf("event %d", i))
			}
			time.Sleep(SendMessageInterval)
		}

		// Best-effort final message (non-blocking to avoid deadlock).
		select {
		case <-ctx.Done():
			return
		default:
			loggerProducer.Info("Completed")
		}
	}()

	// Run the logger (blocking)
	if err = logger.Run(ctx); err != nil && !errors.Is(
		err,
		context.Canceled,
	) {
		_, _ = fmt.Fprintf(os.Stderr, "error: %v\n", err)
	}

	// Optional graceful wait
	select {
	case <-ctx.Done():
	case <-time.After(GracefulShutdownTimeout):
	}
}
