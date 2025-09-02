package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// MessagesChannelBufferSize is the size of the message channel buffer
	MessagesChannelBufferSize = 512

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
	if *generateClipEmbeddingsPath == "" {
		log.Fatal("missing required flag: --generate-clip-embeddings-path")
	}
	if *runClipPath == "" {
		log.Fatal("missing required flag: --run-clip-path")
	}

	// Channel for messages
	msgCh := make(chan *internallog.Message, MessagesChannelBufferSize)

	// Initialize the writer
	writer, err := internallog.NewDefaultWriter(msgCh, *logDebug)
	if err != nil {
		log.Fatalf("failed to initialize writter: %v", err)
	}

	// Initialize the CLIP handler
	clipHandler, err := internalclip.NewClipHandler(
		msgCh,
		*generateClipEmbeddingsPath,
		*runClipPath,
		&internalclip.PositiveLabels,
		&internalclip.NegativeLabels,
		*logDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize clip handler: %v", err)
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

	// Generate the CLIP embeddings
	if err = clipHandler.GenerateEmbeddings(); err != nil {
		log.Fatalf("failed to generate clip embeddings: %v", err)
		return
	}

	// Initialize the CLIP goroutine
	g.Go(
		func() error {
			return clipHandler.ReadIncomingClassifications(ctx)
		},
	)

	// Initialize a goroutine to print the classifications at regular intervals
	g.Go(
		func() error {
			for {
				select {
				case <-ctx.Done():
					return nil
				default:
					classification := clipHandler.GetClassification()
					if classification == nil {
						fmt.Println("No classification found")
					} else {
						fmt.Println(
							fmt.Sprintf(
								"Classification found for label '%s' with confidence %.2f",
								classification.Label,
								classification.Confidence,
							),
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
		// Timeout reached, close channels
		close(msgCh)
	}

}
