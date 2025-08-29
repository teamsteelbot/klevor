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
)

func main() {
	// Define flags (argument parser style)
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	logTimeout := flag.Duration(
		"shutdown-timeout",
		5*time.Second,
		"Graceful shutdown timeout",
	)
	flag.Parse()

	// Channel for messages
	msgCh := make(chan *internallog.Message, 128)

	writer, err := internallog.NewDefaultWriter(msgCh, *logDebug)
	if err != nil {
		log.Fatalf("init logger: %v", err)
	}

	ctx, cancel := context.WithCancel(context.Background())

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

	if err = writer.WriteReceivedMessages(ctx); err != nil && !errors.Is(
		err,
		context.Canceled,
	) {
		_, err = fmt.Fprintf(os.Stderr, "logger error: %v\n", err)
		if err != nil {
			return
		}
	}

	// Optional graceful wait
	select {
	case <-ctx.Done():
	case <-time.After(*logTimeout):
	}
}
