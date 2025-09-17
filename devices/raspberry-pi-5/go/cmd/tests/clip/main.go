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
	// ClassificationInterval is the interval between printing the classification
	ClassificationInterval = 100 * time.Millisecond
)

func main() {
	// Define flags
	clipDebug := flag.Bool("clip-debug", false, "Enable Hailo CLIP debug")
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
	if *generateClipEmbeddingsPath == "" {
		log.Fatal("missing required flag: --generate-clip-embeddings-path")
	}
	if *runClipPath == "" {
		log.Fatal("missing required flag: --run-clip-path")
	}

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

	// Initialize the CLIP handler
	clipHandler, err := internalclip.NewDefaultHandler(
		*generateClipEmbeddingsPath,
		*runClipPath,
		internalclip.PositiveLabels,
		internalclip.NegativeLabels,
		logger,
		*clipDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize clip handler: %v", err)
	}

	// Generate the CLIP embeddings
	fmt.Println("Generating CLIP embeddings")
	if err = clipHandler.GenerateEmbeddings(ctx); err != nil {
		stop()
		fmt.Printf("Failed to generate CLIP embeddings: %v\n", err)
		fmt.Println("Stopping all goroutines...")
		
		// Wait for the logger goroutine to finish
		if err = g.Wait(); err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "error: %v\n", err)
		}
		return
	}
	fmt.Println("CLIP embeddings generated successfully")
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
					// Context canceled, return the error
					fmt.Println("Context canceled")
					return ctx.Err()
				default:
					classification, err := clipHandler.GetClassification()
					if err != nil {
						fmt.Printf("failed to get classification: %v\n", err)
					}
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
}
