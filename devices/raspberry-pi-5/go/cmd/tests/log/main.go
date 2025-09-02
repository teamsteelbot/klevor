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
)

const (
	// SimulateShutdownAfter for demonstration purposes, simulate shutdown after this duration
	SimulateShutdownAfter = 5 * time.Second

	// SendMessageInterval is the interval between sending messages
	SendMessageInterval = 10 * time.Millisecond

	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// ChannelBufferSize is the size of the message channel buffer
	ChannelBufferSize = 512
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	flag.Parse()

	// Channel for messages
	msgCh := make(chan *internallog.Message, ChannelBufferSize)

	// Initialize the writer
	writer, err := internallog.NewDefaultWriter(msgCh, *logDebug)
	if err != nil {
		log.Fatalf("failed to intialize writer: %v", err)
	}

	// Create a context that is cancelled on shutdown signal
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Example: simulate shutdown on SIGINT
	go func() {
		// In real code capture os.Signal
		time.Sleep(SimulateShutdownAfter)
		cancel()
	}()

	// Example producer
	go func() {
		for i := 0; i < 100; i++ {
			msgCh <- internallog.NewMessage(
				internallog.CategoryInfo,
				fmt.Sprintf("event %d", i),
				nil,
			)
			time.Sleep(SendMessageInterval)
		}
		close(msgCh)
	}()

	// Read the messages and write them
	if err = writer.WriteReceivedMessages(ctx); err != nil && !errors.Is(
		err,
		context.Canceled,
	) {
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
