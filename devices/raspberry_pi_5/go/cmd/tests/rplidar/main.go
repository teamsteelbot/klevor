package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// MessagesChannelBufferSize is the size of the message channel buffer
	MessagesChannelBufferSize = 512

	// MeasuresMapBufferSize is the size of the measures map channel buffer
	MeasuresMapBufferSize = 10
)

func main() {
	// Define flags (argument parser style)
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Channel for messages
	msgCh := make(chan *internallog.Message, MessagesChannelBufferSize)

	// Channel for measures map
	measuresMapCh := make(
		chan *map[uint16]*internal.Measure,
		MeasuresMapBufferSize,
	)

	// Initialize the writer
	writer, err := internallog.NewDefaultWriter(msgCh, *logDebug)
	if err != nil {
		log.Fatalf("failed to initialize writter: %v", err)
	}

	// Initialize the Slamtec C1 handler
	rplidarHandler, err := internalrplidar.NewSlamtecC1Handler(
		msgCh,
		measuresMapCh,
		internalrplidar.SlamtecC1BaudRate,
		internalrplidar.SlamtecC1Port,
		true,
		0.0,
		true,
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

	// Initialize a goroutine to print the measures map
	g.Go(
		func() error {
			for measures := range measuresMapCh {
				// Print the measures map
				fmt.Printf("Received measures: %+v\n", measures)
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
	}
}
