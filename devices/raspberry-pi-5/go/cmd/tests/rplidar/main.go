package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// MessagesChannelBufferSize is the size of the message channel buffer
	MessagesChannelBufferSize = 512

	// RotationCompletedChannelBufferSize is the size of the rotation completed channel buffer
	RotationCompletedChannelBufferSize = 10
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Channel for messages
	msgCh := make(chan *internallog.Message, MessagesChannelBufferSize)

	// Channel for rotation completed signals
	rotationCompletedCh := make(
		chan internalrplidar.RotationCompleted,
		RotationCompletedChannelBufferSize,
	)

	// Initialize the writer
	writer, err := internallog.NewDefaultWriter(msgCh, *logDebug)
	if err != nil {
		log.Fatalf("failed to initialize writter: %v", err)
	}

	// Initialize the Slamtec C1 handler
	rplidarHandler, err := internalrplidar.NewSlamtecC1Handler(
		msgCh,
		rotationCompletedCh,
		internalrplidar.SlamtecC1BaudRate,
		internalrplidar.SlamtecC1Port,
		true,
		0.0,
		*logDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize rplidar handler: %v", err)
	}

	// Create a context that is cancelled on shutdown signal
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Initialize the writer goroutine
	g.Go(
		func() error {
			return writer.WriteReceivedMessages(ctx)
		},
	)

	// Initialize the RPLiDAR goroutine
	g.Go(
		func() error {
			return rplidarHandler.ReadIncomingMeasures(ctx)
		},
	)

	// Initialize a goroutine to print the measures on each rotation completed
	g.Go(
		func() error {
			for _ = range rotationCompletedCh {
				// Print that a rotation has been completed
				fmt.Println("Rotation completed")
			}
			return nil
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
		// Timeout reached, close channels
		close(msgCh)
		close(rotationCompletedCh)
	}
}
