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

	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// ClassificationInterval is the interval between printing the classification
	ClassificationInterval = 100 * time.Millisecond
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	generateClipEmbeddingsPath := flag.String(
		"generate-clip-embeddings-path",
		"",
		"Path to the .sh file that generates CLIP embeddings",
	)
	runClipPath := flag.String(
		"run-clip-path",
		"",
		"Path to the .sh file that runs CLIP",
	)
	flag.Parse()

	// Enforce required flags
	if *runClipPath == "" {
		log.Fatal("missing required flag: --run-clip-path")
	}

	// Initialize the logger
	logger := internallog.NewDefaultLogger(*logDebug)

	// Initialize the CLIP handler
	clipHandler, err := internalclip.NewDefaultHandler(
		*generateClipEmbeddingsPath,
		*runClipPath,
		&internalclip.PositiveLabels,
		&internalclip.NegativeLabels,
		logger,
	)
	if err != nil {
		log.Fatalf("failed to initialize clip handler: %v", err)
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

	// Generate the CLIP embeddings
	if *generateClipEmbeddingsPath == "" {
		fmt.Println("Skipping CLIP embeddings generation")
	} else {
		fmt.Println("Generating CLIP embeddings")
		if err = clipHandler.GenerateEmbeddings(); err != nil {
			// Wait for the writer goroutine to finish
			fmt.Println("Error generating CLIP embeddings:", err)
			stop()
			if err = g.Wait(); err != nil {
				_, _ = fmt.Fprintf(os.Stderr, "error: %v\n", err)
			}
			return
		}
		fmt.Println("CLIP embeddings generated successfully")
	}
	defer stop()

	// Initialize the CLIP goroutine
	g.Go(
		func() error {
			return clipHandler.Run(ctx, stop)
		},
	)

	// Initialize a goroutine to print the classifications at regular intervals
	g.Go(
		func() error {
			for {
				select {
				case <-ctx.Done():
					return ctx.Err()
				default:
					classification := clipHandler.GetClassification()
					if classification == nil {
						fmt.Println("No classification found")
					} else {
						fmt.Printf(
							"Classification found for label '%s' with confidence %.2f\n",
							classification.Label,
							classification.Confidence,
						)
					}
					time.Sleep(ClassificationInterval)
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
