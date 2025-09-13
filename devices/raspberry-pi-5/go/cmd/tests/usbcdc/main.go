package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"log"
	"os/signal"
	"syscall"
	"time"

	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
	"golang.org/x/sync/errgroup"
)

const (
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second
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

	// Initialize the USB-CDC handler
	usbCDCHandler, err := internalusbcdc.NewDefaultHandler(
		internalusbcdc.BaudRate,
		logger,
	)
	if err != nil {
		log.Fatalf("failed to initialize usb-cdc handler: %v", err)
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

	// Initialize the USB-CDC goroutine
	g.Go(
		func() error {
			return usbCDCHandler.Run(ctx, stop)
		},
	)

	// Wait for the goroutines to finish
	if err := g.Wait(); err != nil && !errors.Is(err, context.Canceled) {
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
