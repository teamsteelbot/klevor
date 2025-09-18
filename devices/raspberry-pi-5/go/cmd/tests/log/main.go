package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"golang.org/x/sync/errgroup"

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
)

const (
	// SimulateShutdownAfter for demonstration purposes, simulate shutdown after this duration
	SimulateShutdownAfter = 5 * time.Second

	// SendMessageInterval is the interval between sending messages
	SendMessageInterval = 10 * time.Millisecond

	// TotalMessages to send before stopping
	TotalMessages = 100
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Initialize the logger
	logger, err := internallog.NewDefaultLogger()
	if err != nil {
		log.Fatalf("failed to create logger: %v\n", err)
	}

	// Context canceled on SIGINT/SIGTERM.
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Initialize the logger goroutine
	g.Go(
		func() error {
			return logger.Run(ctx, stop)
		},
	)

	// Wait a moment to ensure the logger is ready
	fmt.Println("Waiting for logger to be ready...")
	if err := logger.WaitUntilReady(ctx); err != nil {
		log.Fatalf("failed to wait for logger readiness: %v", err)
	}
	fmt.Println("Logger is ready")

	// Create a new logger producer
	loggerProducer, err := logger.NewProducer("TEST_PRODUCER", *logDebug)
	if err != nil {
		log.Fatalf("failed to create logger producer: %v\n", err)
	}

	// Simulate shutdown on SIGINT
	g.Go(
		func() error {
			time.Sleep(SimulateShutdownAfter)
			stop()
			return nil
		},
	)

	// Example usage of the logger producer in a separate goroutine
	g.Go(
		func() error {
			defer loggerProducer.Close()

			// Send messages
			for i := range TotalMessages {
				select {
				case <-ctx.Done():
					// Context canceled, return
					fmt.Println("Context canceled, stopping message sending")
					return ctx.Err()
				default:
					loggerProducer.Info(fmt.Sprintf("event %d", i))
				}
				time.Sleep(SendMessageInterval)
			}

			// Best-effort final message (non-blocking to avoid deadlock).
			select {
			case <-ctx.Done():
				return nil
			default:
				loggerProducer.Info("Completed")
			}
			return nil
		},
	)

	// Wait for the goroutines to finish
	if err := g.Wait(); err != nil && !errors.Is(err, context.Canceled) {
		_, err = fmt.Fprintf(os.Stderr, "error: %v\n", err)
		if err != nil {
			return
		}
	}
}
