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

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// RPLiDARPrintInterval is the interval between printing the RPLiDAR measures
	RPLiDARPrintInterval = 100 * time.Millisecond
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Initialize the logger
	logger, err := internallog.NewDefaultLogger(*logDebug)
	if err != nil {
		log.Fatalf("failed to create logger: %v\n", err)
	}

	// Initialize the Slamtec C1 handler
	rplidarHandler, err := internalrplidar.NewSlamtecC1Handler(logger)
	if err != nil {
		log.Fatalf("failed to initialize rplidar handler: %v", err)
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

	// Initialize the RPLiDAR goroutine
	g.Go(
		func() error {
			return rplidarHandler.Run(ctx, stop)
		},
	)

	// Initialize a goroutine to print the measures on each rotation completed
	g.Go(
		func() error {
			// Listen for rotation completed events
			for {
				select {
				case <-ctx.Done():
					// Context canceled, return the error
					fmt.Println("Context canceled")
					return ctx.Err()
				default:
					// Print the measures
					fmt.Println(*rplidarHandler.GetMeasures())

					// Print the measures every RPLiDARPrintInterval
					time.Sleep(RPLiDARPrintInterval)
				}
			}
		},
	)

	// Wait for the goroutines to finish
	if err = g.Wait(); err != nil && !errors.Is(err, context.Canceled) {
		_, err = fmt.Fprintf(os.Stderr, "error: %v\n", err)
		if err != nil {
			return
		}
	}

	// Optional graceful wait
	select {
	case <-ctx.Done():
	case <-time.After(GracefulShutdownTimeout):
	}
}
